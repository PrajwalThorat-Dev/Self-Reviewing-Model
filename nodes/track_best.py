import logging
from state.schema import AgentState

logger=logging.getLogger(__name__)

def track_best_node(state: AgentState) -> dict:
    current_score=state["score"]
    current_draft=state["draft"]
    
    best_score=state.get("best_score",0.0)
    
    #only update if this draft scored higher than anything seen so far
    
    if current_score > best_score:
        logger.info(
            "New best draft found(score %s > previous best %s)",
            current_score, best_score,
        )
        return{
            "best_draft":current_draft,
            "best_score":current_score,
        }
        
    logger.info(
        "Current draft (score %s) did not beat best so far (score %s)",
        current_score, best_score,
    )
    
    #no update - keep existing best_draft/best_score untouched
    
    return {}