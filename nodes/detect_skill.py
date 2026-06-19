import logging
import re

from langchain_groq import ChatGroq
from state.schema import AgentState
from config.settings import GROQ_API_KEY,GROQ_MODEL_NAME

logger = logging.getLogger(__name__)

# keywords that strongly suggest a code-related request
CODE_KEYWORDS = [
    "function", "bug", "error", "script", "debug", "exception",
    "stack trace", "compile", "python", "javascript", "java", "sql",
    "code", "syntax", "variable", "loop", "class ", "def ",
]


llm=ChatGroq(
    api_key=GROQ_API_KEY,
    model=GROQ_MODEL_NAME,
    temperature=0,
    max_tokens=10,
)

def heuristic_check(user_input: str)->str:
    text=user_input.lower()

    # code fences are a near-certain signal
    if "```" in user_input:
        return "code"
    
    keyword_hit=any(keyword in text for keyword in CODE_KEYWORDS)

    if keyword_hit:
        return "code"
    
    # no strong signal either way — let the LLM decide
    return "unclear"

def llm_classify(user_input: str)->str:
    prompt=f"""
Classify this request as either "code" or "general".

Request:
{user_input}

Respond with Exactly one word: code or general
"""
    logger.info("Heuristic was unclear, falling back to LLM classification")
    response=llm.invoke(prompt)
    answer=response.content.strip().lower()

    if "code" in answer:
        return "code"
    return "general"

def detect_skill_node(state: AgentState)->dict:
    # respects manual override — only auto-detects if skill wasn't already set
    if state.get("skill"):
        logger.info("Skill already set manually: %s", state["skill"])
        return{}
    
    result=heuristic_check(state["user_input"])
    
    if result == "unclear":
        result=llm_classify(state["user_input"])
    else:
        logging.info("Heuristic detected skill: %s", result)

    return {"skill": result}
     
