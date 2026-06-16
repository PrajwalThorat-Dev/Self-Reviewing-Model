import logging
from langchain_groq import ChatGroq
from state.schema import AgentState, Critique
from config.settings import GROQ_API_KEY, GROQ_MODEL_NAME

logger = logging.getLogger(__name__)

llm = ChatGroq(
    api_key=GROQ_API_KEY,
    model=GROQ_MODEL_NAME,
    temperature=0,
)

# json_mode for structured output for smaller Groq models
llm_structured = llm.with_structured_output(Critique, method="json_mode")


def critique_node(state: AgentState) -> dict:
    fact_check_summary = "No factual issues found."

    if state.get("fact_check") and not state["fact_check"]["is_accurate"]:
        fact_check_summary = f"Flagged claims: {state['fact_check']['flagged_claims']}"

    # everything below is now OUTSIDE the if block — runs regardless
    prompt = f"""
You are a strict reviewer evaluating the quality of a draft response.

Original request:
{state["user_input"]}

Draft:
{state["draft"]}

Fact-check result:
{fact_check_summary}

Evaluate the draft on clarity, completeness, and correctness.
List strengths, weaknesses, and concrete suggestions for improvement.
Give a score from 0 to 10.

Respond ONLY in valid JSON with EXACTLY this structure, no extra wrapping keys:
{{
  "strengths": ["..."],
  "weaknesses": ["..."],
  "suggestions": ["..."],
  "score": 0.0
}}
"""

    logger.info("Sending draft for critique (iteration %s)", state["iteration"])
    result: Critique = llm_structured.invoke(prompt)
    logger.info("RAW CRITIQUE RESULT: %s", result)

    if "score" not in result and len(result) == 1:
        result = next(iter(result.values()))

    result.setdefault("strengths", [])
    result.setdefault("weaknesses", [])
    result.setdefault("suggestions", [])
    result.setdefault("score", 0.0)

    score = result["score"]
    logger.info("Critique score: %s", score)

    return {
        "critique": result,
        "score": score,
    }