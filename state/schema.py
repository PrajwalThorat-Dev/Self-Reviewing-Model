from typing import TypedDict, Optional, Union

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
    skill: Optional[str]                                    # set by review_agent via load_skill
    draft: str
    blocked: bool
    critique: Optional[Union[Critique, CodeReviewResult]]  # shape depends on active skill
    score: float
    best_draft: Optional[str]
    best_score: float
    iteration: int
    max_iterations: int
    final_output: Optional[str]
