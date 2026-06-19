import logging
from state.schema import AgentState
from guardrails.input_guardrail import check_input

logger=logging.getLogger(__name__)

def guard_input_node(state: AgentState)->dict:
    result=check_input(state["user_input"])

    if result["blocked"]:
        logger.info("Input blocked: %s", result["block_reason"])
    else:
        logger.info("Input passed guardrails check")

    return result