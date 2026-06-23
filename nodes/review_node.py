import logging
from langchain.agents import create_agent
from langchain_groq import ChatGroq
from state.schema import AgentState
from tools.skill_loader import load_skill
from tools.code_analysis import check_syntax, run_ruff
from middleware.content_filter import ContentFilterMiddleware
from config.settings import GROQ_API_KEY, GROQ_TOOL_MODEL_NAME

logger = logging.getLogger(__name__)

# model for tool-calling and reasoning inside the agent
llm = ChatGroq(
    api_key=GROQ_API_KEY,
    model=GROQ_TOOL_MODEL_NAME,
    temperature=0,
    max_tokens=2048,
)

# lightweight model for content filter classification only
filter_llm = ChatGroq(
    api_key=GROQ_API_KEY,
    model=GROQ_TOOL_MODEL_NAME,
    temperature=0,
    max_tokens=10,
)

# create the review agent once at module level — not inside the function
review_agent = create_agent(
    model=llm,
    tools=[load_skill, run_ruff],
    middleware=[
        ContentFilterMiddleware(model=filter_llm),
    ],
    system_prompt=(
        "You are a strict code and content reviewer. "
        "First call load_skill with the appropriate skill name ('code' or 'general') "
        "based on what the user submitted. "
        "Then review the draft thoroughly using the loaded criteria. "
        "If reviewing code, use run_ruff to check for linting issues. "
        "Return your final review as valid JSON with keys: "
        "strengths, bugs or weaknesses, suggestions, score (0-10)."
    ),
)


def review_node(state: AgentState) -> dict:
    draft = state["draft"]

    # deterministic syntax check — always runs, free, no API call
    syntax_result = check_syntax(draft)
    syntax_note = ""
    if not syntax_result["is_valid"]:
        syntax_note = f"\nSyntax errors found: {syntax_result['errors']}"
        logger.info("Syntax errors detected: %s", syntax_result["errors"])

    prompt = f"""Review the following submission.

Original request:
{state["user_input"]}

Draft:
{draft}
{syntax_note}

Call load_skill first, then provide your structured review as JSON.
"""

    logger.info("Invoking review agent (iteration %s)", state["iteration"])

    response = review_agent.invoke({
    "messages": [{"role": "user", "content": prompt}]
    })

    messages = response["messages"]
    last_message = messages[-1]
    raw_content = last_message.content

    # structural block detection — blocked responses have exactly 2 messages
    # (HumanMessage + AIMessage) with no tool calls in between
    is_blocked = (
        len(messages) == 2
        and not any(hasattr(m, "tool_calls") and m.tool_calls for m in messages)
    )

    if is_blocked:
        logger.info("Request blocked by middleware — routing to finalize")
        return {
            "blocked": True,
            "final_output": raw_content,
            "score": 0.0,
            "critique": None,
        }

    logger.info("Review agent raw response: %s", raw_content)

    # parse the JSON response from the agent
    import json
    import re

    # strip markdown code fences if the model wrapped JSON in them
    cleaned = re.sub(r"```(?:json)?\n?", "", raw_content).replace("```", "").strip()

    try:
        result = json.loads(cleaned)
    except json.JSONDecodeError:
        logger.info("JSON parse failed, using fallback empty review")
        result = {
            "strengths": [],
            "weaknesses": [],
            "bugs": [],
            "suggestions": [],
            "score": 0.0,
        }

    # merge syntax errors directly into bugs/weaknesses — guaranteed ground truth
    if not syntax_result["is_valid"]:
        key = "bugs" if "bugs" in result else "weaknesses"
        result[key] = syntax_result["errors"] + result.get(key, [])

    # defensive fallbacks
    result.setdefault("strengths", [])
    result.setdefault("weaknesses", [])
    result.setdefault("bugs", [])
    result.setdefault("suggestions", [])
    result.setdefault("score", 0.0)

    score = float(result.get("score", 0.0))
    logger.info("Review complete. Score: %s", score)

    return {
        "critique": result,
        "score": score,
        "skill": result.get("skill", state.get("skill", "general")),
    }