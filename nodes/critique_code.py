import logging
from langchain_groq import ChatGroq
from state.schema import AgentState, CodeReviewResult
from skills.registry import get_skill
from config.settings import GROQ_API_KEY, GROQ_MODEL_NAME

logger = logging.getLogger(__name__)

llm=ChatGroq(
    api_key=GROQ_API_KEY,
    model=GROQ_MODEL_NAME,
    temperature=0,
    max_tokens=1024,
)

llm_structured=llm.with_structured_output(CodeReviewResult, method='json_mode')

def critique_code_node(state: AgentState)->dict:
    skill=get_skill(state['skill']) #fetches CodeReviewSkill instance
    
    fact_check_summary="No factual issues found."
    
    if state.get("fact_check") and not state['fact_check']["is_accurate"]:
        fact_check_summary=f"Flagged claims: {state['fact_check']['flagged_claims']}"
        
    prompt=skill.build_critique_prompt(
        user_input=state["user_input"],
        draft=state["draft"],
        fact_check_summary=fact_check_summary,
    )
    
    logger.info("Sending code draft for critique (iteration %s)",state["iteration"])
    result = llm_structured.invoke(prompt)
    logger.info("RAW CODE CRITIQUE RESULT: %s", result)

    # unwrap if model nested everything under a single wrapper key
    if "score" not in result and len(result) == 1:
        result = next(iter(result.values()))

    # defensive fallbacks in case the model dropped a field
    result.setdefault("strengths", [])
    result.setdefault("bugs", [])
    result.setdefault("suggestions", [])
    result.setdefault("score", 0.0)

    score = result["score"]
    
    logger.info("Code critique score: %s", score)
    
    return{
        "critique":result,
        "score": score,
    }
    
    