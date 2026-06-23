# prompt templates for the code review skill

GENERATE_PROMPT = """You are a software engineer responding to a coding request.

Request:
{user_input}

Provide a clear, working solution with brief inline comments only where logic is non-obvious.
"""

CRITIQUE_PROMPT = """You are a strict code reviewer evaluating a code submission.

Original request:
{user_input}

Code submitted:
{draft}

Static analysis findings:
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

REFINE_PROMPT = """You are fixing code based on a reviewer's feedback.

Original request:
{user_input}

Current code:
{draft}

Keep these strengths intact:
{strengths}

Fix these bugs:
{bugs}

Apply these suggestions:
{suggestions}

{correction_notes}

Write the corrected code only. Do not include explanations or commentary.
"""