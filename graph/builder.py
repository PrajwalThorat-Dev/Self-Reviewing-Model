from langgraph.graph import StateGraph, END

from state.schema import AgentState
from nodes.generate import generate_node
from nodes.fact_check import fact_check_node
from nodes.critique import critique_node
from nodes.refine import refine_node
from nodes.finalize import finalize_node


def should_continue(state: AgentState) -> str:
    # if max iterations hit, force finalize
    if state["iteration"] >= state["max_iterations"]:
        return "finalize"

    # if score is above threshold, finalize
    if state["score"] >= 7.0:
        return "finalize"

    # otherwise refine
    return "refine"


def build_graph() -> StateGraph:
    graph = StateGraph(AgentState)

    # register nodes
    graph.add_node("generate", generate_node)
    graph.add_node("fact_check", fact_check_node)
    graph.add_node("critique", critique_node)
    graph.add_node("refine", refine_node)
    graph.add_node("finalize", finalize_node)

    # entry point
    graph.set_entry_point("generate")

    # fixed edges
    graph.add_edge("generate", "fact_check")
    graph.add_edge("fact_check", "critique")
    graph.add_edge("refine", "fact_check")      # after refine, re-check facts

    # conditional edge after critique
    graph.add_conditional_edges(
        "critique",
        should_continue,
        {
            "refine": "refine",
            "finalize": "finalize",
        }
    )

    # finalize exits the graph
    graph.add_edge("finalize", END)

    return graph.compile()