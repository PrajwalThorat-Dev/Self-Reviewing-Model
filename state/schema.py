import logging
from typing import TypedDict, Optional, Union

logger=logging.getLogger(__name__)

#Used by the "code" skill critique node
class CodeReviewResult(TypedDict):
    strengths: list[str]
    bugs: list[str]
    suggestions: list[str]
    score: float

#Used by the "general" skill critique node
class Critique(TypedDict):
    strengths: list[str]
    weaknesses: list[str]
    suggestions: list[str]
    score: float

#Shared across all skills
class FactCheckResult(TypedDict):
    is_accurate: bool
    flagged_claims: list[str]  # claims that seem wrong
    corrections: list[str]  # corrections for the flagged claims


class AgentState(TypedDict):
    user_input: str
    skill: str #general or code Choosed at run time
    draft:str
    fact_check: Optional[FactCheckResult]
    critique: Optional[Union[Critique, CodeReviewResult]] #depends on which skill choose
    score: float
    best_draft: Optional[str]
    best_score: float
    iteration: int
    max_iterations: int
    final_output: Optional[str]
