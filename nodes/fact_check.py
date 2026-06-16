import logging
from langchain_groq import ChatGroq
from state.schema import AgentState, FactCheckResult
from config.settings import GROQ_API_KEY, GROQ_MODEL_NAME

logger=logging.getLogger(__name__)

llm=ChatGroq(
    api_key=GROQ_API_KEY,
    model=GROQ_MODEL_NAME,
    temperature=0,
)

llm_structured=llm.with_structured_output(FactCheckResult, method="json_mode")



def fact_check_node(state: AgentState) -> dict:
    prompt = f"""
You are a fact-checking assistant. Review the following draft for factual errors.

Draft:
{state["draft"]}

Identify any claims that are factually incorrect or unverifiable.

Respond ONLY in valid JSON with EXACTLY this structure, no extra wrapping keys:
{{
  "is_accurate": true,
  "flagged_claims": ["..."],
  "corrections": ["..."]
}}

If everything is accurate, return is_accurate=true with empty lists.
"""
    # nodes/fact_check.py
    result: FactCheckResult = llm_structured.invoke(prompt) 
    logger.info("RAW FACT CHECK RESULT: %s", result)

    # unwrap if model nested under a single wrapper key
    if "is_accurate" not in result and len(result) == 1:
        result = next(iter(result.values()))

    # fallback defaults if still malformed
    result.setdefault("is_accurate", True)
    result.setdefault("flagged_claims", [])
    result.setdefault("corrections", [])

    return {
        "fact_check": result,
    }