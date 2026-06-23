import logging
from langchain_ollama import ChatOllama
from state.schema import AgentState
from skills.registry import get_skill
from config.settings import LOCAL_MODEL_NAME

logger = logging.getLogger(__name__)


llm =ChatOllama(model=LOCAL_MODEL_NAME,temperature=0.7)

def generate_node(state: AgentState) -> dict:

      if state.get("skill") and state["skill"] in ("code",):
            # skill is set and known — delegate prompt to skill object
            skill=get_skill(state["skill"])
            prompt=skill.build_generate_prompt(state["user_input"])
            logger.info("Generating draft using skill: %s", state["skill"])
      else:
            # general skill or skill not yet set — use raw user input
            prompt=state["user_input"]
            logger.info("Generating draft using general prompt")

      response=llm.invoke(prompt)

      return {
            "draft":response.content,
            "iteration":state["iteration"]+1
      }

