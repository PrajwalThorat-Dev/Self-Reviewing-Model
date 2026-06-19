import logging
from config.settings import SCORE_THRESHOLD
from langgraph.graph import StateGraph, START, END
from state.schema import AgentState

from nodes.generate import generate_node
from nodes.guard_input import guard_input_node
from nodes.blocked import blocked_node
from nodes.fact_check import fact_check_node
from nodes.critique import critique_node
from nodes.critique_code import critique_code_node
from nodes.refine import refine_node
from nodes.track_best import track_best_node
from nodes.finalize import finalize_node
from nodes.detect_skill import detect_skill_node


logger=logging.getLogger(__name__)

def input_allowed(state: AgentState)->str:
    # reads state["blocked"] (set by guard_input_node) to decide the next path
    if state["blocked"]:
        return "blocked"
    return "detect_skill"

def should_continue(state: AgentState) -> str:
    # if max iterations hit, force finalize
    if state["iteration"] >= state["max_iterations"]:
        return "finalize"

    # if score is above threshold, finalize
    if state["score"] >= SCORE_THRESHOLD:
        return "finalize"

    # otherwise refine
    return "refine"


def route_critique(state: AgentState) -> str:
    # reads state["skill"] to decide which critique node handles this draft
    if state["skill"] == "code":
        return "critique_code"
    return "critique"


def build_graph() -> StateGraph:
    
    graph = StateGraph(AgentState)

    # register nodes
    graph.add_node("guard_input",guard_input_node)
    graph.add_node("blocked",blocked_node)
    graph.add_node("detect_skill",detect_skill_node)
    graph.add_node("generate", generate_node)
    graph.add_node("fact_check", fact_check_node)
    graph.add_node("critique", critique_node)
    graph.add_node("critique_code", critique_code_node)
    graph.add_node("refine", refine_node)
    graph.add_node("track_best", track_best_node)
    graph.add_node("finalize", finalize_node)
    

    # entry point
    graph.add_edge(START, "guard_input")

    # conditional edge — blocked input skips the entire pipeline
    graph.add_conditional_edges(
        "guard_input",
        input_allowed,
        {
            "blocked": "blocked",
            "detect_skill": "detect_skill",
        },
    )

    # fixed edges
    graph.add_edge("detect_skill", "generate")
    graph.add_edge("generate", "fact_check")
    
    # conditional edge — routes to the correct critique node based on state["skill"]
    graph.add_conditional_edges(
        "fact_check",
        route_critique,{
            "critique":"critique",
            "critique_code":"critique_code",
        },
    )
    
    # both critique paths now flow through track_best first
    graph.add_edge("critique", "track_best")
    graph.add_edge("critique_code", "track_best")

    # should_continue runs only after best draft is recorded
    graph.add_conditional_edges(
        "track_best",
        should_continue,
        {
            "refine": "refine",
            "finalize": "finalize",
        },
    )
    graph.add_edge("refine", "fact_check")      # after refine, re-check facts

    # finalize exits the graph
    graph.add_edge("finalize", END)
    graph.add_edge("blocked", END)

    logger.info("Graph built successfully")
    return graph.compile()