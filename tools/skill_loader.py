from langchain_core.tools import tool
from prompts import code_review as code_reveiw_prompts
from prompts import general as general_prompts

# maps skill names to their prompt modules
SKILL_PROMPTS={
    "code":code_reveiw_prompts,
    "general":general_prompts,
}

@tool
def load_skill(skill_name: str)->str:
    """
    Load specialized reveiw criteria for a specific domain.
    Available skills:
    - code: Reviews Python code for bugs, style, and correctness
    - general: Reviews written responses for clarity and completeness
    Use this at the start of your review to load the right evaluation criteria.
    Returns the critique prompt template for the requested skill.
    """

    prompts=SKILL_PROMPTS.get(skill_name)

    if prompts is None:
        # fallback to general if unknown skill requested
        prompts=general_prompts
    
    return prompts.CRITIQUE_PROMPT