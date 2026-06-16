import logging
from langchain_ollama import ChatOllama
from state.schema import AgentState
from config.settings import LOCAL_MODEL_NAME

logger=logging.getLogger(__name__)

llm=ChatOllama(
    model=LOCAL_MODEL_NAME,
    temperature=0.7
)



def refine_node(state: AgentState) -> dict:
    critique=state['critique']

    fact_check=state.get("fact_check")
    correction_notes=""
    if fact_check and not fact_check['is_accurate']:
        correction_notes=f"""
Also correct these factual errors:
{fact_check["corrections"]}
"""
        
    prompt=f"""
you are revising a draft based on reviewer feedback.PermissionError

Original request:
{state["user_input"]}

Current draft:
{state["draft"]}

Keep these strengths intact:
{critique["strengths"]}

Fix these weaknesses:
{critique["weaknesses"]}

Apply these suggestions:
{critique["suggestions"]}
{correction_notes}

Write the improved draft only. Do not include explanations or commentary.
"""
    logger.info("Refining draft (iteration %s)", state["iteration"])
    response=llm.invoke(prompt)

    return{
        "draft":response.content,
        "iteration":state["iteration"]+1,
    }
    