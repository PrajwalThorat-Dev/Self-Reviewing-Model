from typing import TypedDict, Optional

class Critique(TypedDict):
    strengths: list[str]
    weaknesses: list[str]
    suggestions: list[str]
    score: float

class FactCheckResult(TypedDict):
    is_accurate: bool
    flagged_claims: list[str]  # claims that seem wrong
    corrections: list[str]  # corrections for the flagged claims


class AgentState(TypedDict):
    user_input: str
    draft:str
    fact_check: Optional[FactCheckResult]
    critique: Optional[Critique]
    score: float
    iteration: int
    max_iterations: int
    final_output: Optional[str]

initial_state: AgentState = {
    "user_input": "Explain how transformers work",
    "draft": "",
    "fact_check": None,
    "critique": None,
    "score": 0.0,
    "iteration": 0,
    "max_iterations": 3,
    "final_output": None,
}