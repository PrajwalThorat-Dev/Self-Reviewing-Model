import logging
from state.schema import AgentState

logger=logging.getLogger(__name__)

def blocked_node(state: AgentState) -> dict:
    reason=state.get("block_reason", "Request was blocked by a guardrail.")

    logger.info("Run terminated by guardrail: %s", reason)

    return {
        "final_output": f"This request could not be processed. {reason}",
    }