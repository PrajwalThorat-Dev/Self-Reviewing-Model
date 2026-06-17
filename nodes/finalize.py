import logging
from state.schema import AgentState

logger=logging.getLogger(__name__)

def finalize_node(state: AgentState) -> dict:
    logger.info("Finalizing output. Best score achieved: %s (after %s iteration(s))",
        state["best_score"],
        state["iteration"],
        )
    
    return{
        "final_output":state["best_draft"],
    }