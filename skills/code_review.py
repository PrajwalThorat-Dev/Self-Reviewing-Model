from skills.base import BaseSkill

class CodeReviewSkill(BaseSkill):
    name="code"
    
    def build_generate_prompt(self, user_input: str) -> str:
         # asks the LLM to produce code or an explanation, framed for a code-review context
        return f"""You are a software engineer responding to a coding request.

Request:
{user_input}

Provide a clear, working solution. Include brief inline comments only where logic is non-obvious.
"""

    def build_critique_prompt(self, user_input: str, draft: str, fact_check_summary: str) -> str:
        # asks the LLM to review code specifically for bugs, not general writing quality
        return f"""You are a strict code reviewer evaluating a code submission.

Original request:
{user_input}

Code submitted:
{draft}

Fact-check result:
{fact_check_summary}

Review the code for correctness, bugs, edge cases, and readability.
List strengths, bugs found, and concrete suggestions for improvement.
Give a score from 0 to 10.

Respond ONLY in valid JSON with EXACTLY this structure, no extra wrapping keys:
{{
  "strengths": ["..."],
  "bugs": ["..."],
  "suggestions": ["..."],
  "score": 0.0
}}
"""

    def build_refine_prompt(self, user_input:str, draft:str, critique:dict, correction_notes:str)->str:
        # reads "bugs" specifically, not "weaknesses" — matches CodeReviewResult shape
        return f"""You are fixing code based on a reviewer's feedback.

Original request:
{user_input}

Current code:
{draft}

Keep these strengths intact:
{critique["strengths"]}

Fix these bugs:
{critique["bugs"]}

Apply these suggestions:
{critique["suggestions"]}
{correction_notes}

Write the corrected code only. Do not include explanations or commentary.
"""