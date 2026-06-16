import logging
from state.schema import AgentState

logger=logging.getLogger(__name__)

def finalize_node(state: AgentState) -> dict:
    logger.info("Finalizing output after %s iteration(s) with score %s",
        state["iteration"],
        state["score"],
        )
    
    return{
        "final_output":state["draft"]
    }