import logging
from config.settings import SCORE_THRESHOLD
from langgraph.graph import StateGraph, START, END

from state.schema import AgentState
from nodes.generate import generate_node
from nodes.fact_check import fact_check_node
from nodes.critique import critique_node
from nodes.critique_code import critique_code_node
from nodes.refine import refine_node
from nodes.finalize import finalize_node


logger=logging.getLogger(__name__)

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
    graph.add_node("generate", generate_node)
    graph.add_node("fact_check", fact_check_node)
    graph.add_node("critique", critique_node)
    graph.add_node("critique_code", critique_code_node)
    graph.add_node("refine", refine_node)
    graph.add_node("finalize", finalize_node)
    

    # entry point
    graph.add_edge(START, "generate")

    # fixed edges
    graph.add_edge("generate", "fact_check")
    
    # conditional edge — routes to the correct critique node based on state["skill"]
    graph.add_conditional_edges(
        "fact_check",
        route_critique,{
            "critique":"critique",
            "critique_code":"critique_code",
        },
    )
    
    graph.add_conditional_edges(
        "critique",
        should_continue,
        {
            "refine":"refine",
            "finalize":"finalize",
        },
    )
    graph.add_conditional_edges(
        "critique_code",
        should_continue,
        {
            "refine":"refine",
            "finalize":"finalize",
        },
    )
    graph.add_edge("refine", "fact_check")      # after refine, re-check facts

    # finalize exits the graph
    graph.add_edge("finalize", END)

    logger.info("Graph built successfully")
    return graph.compile()