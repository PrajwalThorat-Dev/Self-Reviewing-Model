import logging
from langgraph.graph import StateGraph, START, END

from state.schema import AgentState
from nodes.generate import generate_node
from nodes.review_node import review_node
from nodes.track_best import track_best_node
from nodes.refine import refine_node
from nodes.finalize import finalize_node
from config.settings import SCORE_THRESHOLD


logger=logging.getLogger(__name__)

def should_continue(state: AgentState) -> str:
    # if middleware blocked the request, finalize immediately
    if state.get("blocked"):
        return "finalize"
    
    # if max iterations hit, force finalize
    if state["iteration"] >= state["max_iterations"]:
        return "finalize"

    # if score is above threshold, finalize
    if state["score"] >= SCORE_THRESHOLD:
        return "finalize"

    # otherwise refine
    return "refine"


def build_graph() -> StateGraph:
    
    graph = StateGraph(AgentState)

    # register nodes
    graph.add_node("generate", generate_node)
    graph.add_node("review", review_node)
    graph.add_node("track_best", track_best_node)
    graph.add_node("refine", refine_node)
    graph.add_node("finalize", finalize_node)
    

    # entry point
    graph.add_edge(START, "generate")

    # fixed edges
    graph.add_edge("generate", "review")
    graph.add_edge("refine", "review")

    # review always goes to track_best
    graph.add_edge("review", "track_best")

    # track_best decides: refine or finalize
    graph.add_conditional_edges(
        "track_best",
        should_continue,
        {
            "refine": "refine",
            "finalize": "finalize",
        },
    )

    # finalize exits
    graph.add_edge("finalize", END)

    logger.info("Graph built successfully")
    return graph.compile()