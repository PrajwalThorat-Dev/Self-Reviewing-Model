import logging
from langchain_groq import ChatGroq
from langchain.agents.middleware import AgentMiddleware
from state.schema import AgentState, CodeReviewResult
from skills.registry import get_skill
from tools.code_analysis import check_syntax, run_ruff
from config.settings import GROQ_API_KEY, GROQ_MODEL_NAME, GROQ_TOOL_MODEL_NAME

logger = logging.getLogger(__name__)

llm=ChatGroq(
    api_key=GROQ_API_KEY,
    model=GROQ_MODEL_NAME,
    temperature=0,
    max_tokens=1024,
)

llm_tool = ChatGroq(
    api_key=GROQ_API_KEY,
    model=GROQ_TOOL_MODEL_NAME,
    temperature=0,
    max_tokens=1024,
)

#bind ruff as an available tool
llm_with_tools=llm_tool.bind_tools([run_ruff])

#separate structured output LLM 
llm_structured=llm.with_structured_output(CodeReviewResult, method='json_mode')

def critique_code_node(state: AgentState)->dict:
    skill=get_skill(state['skill']) #fetches CodeReviewSkill instance
    
    syntax_result=check_syntax(state["draft"])
    logger.info("Syntax check result: valid=%s", syntax_result["is_valid"])


    fact_check_summary="No factual issues found."
    if state.get("fact_check") and not state['fact_check']["is_accurate"]:
        fact_check_summary=f"Flagged claims: {state['fact_check']['flagged_claims']}"

    #agentic ruff check, LLM decides whether to invoke it
    tool_prompt=f"""You are a code reviewer analysing the following Python code.

Code:
{state["draft"]}

You have access to a ruff linter tool. If you think the code needs deeper static analysis
beyond what you can see directly, call the run_ruff tool with the code.
"""
    logger.info("Asking LLM to decide whether to run ruff (iteration %s)", state["iteration"])
    tool_response=llm_with_tools.invoke(tool_prompt)

    #collect ruff findings if the LLM chose to call the tool
    ruff_findings=""
    for tool_call in tool_response.tool_calls:
        if tool_call["name"]=="run_ruff":
            ruff_output=run_ruff.invoke(tool_call["args"])
            logger.info("Ruff tool called by LLM. Output: %s", ruff_output)
            ruff_findings=f"\n Ruff linter findings: \n{ruff_output}"

    if not tool_response.tool_calls:
        logger.info("LLM chose not to call ruff tool")

    
    #build full critique prompt with all findings
    critique_prompt=skill.build_critique_prompt(
        user_input=state["user_input"],
        draft=state["draft"],
        fact_check_summary=fact_check_summary+ruff_findings,
    )
    
    #structured critique from Groq
    logger.info("Sending code draft for critique (iteration %s)",state["iteration"])
    result:CodeReviewResult = llm_structured.invoke(critique_prompt)

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
    
    