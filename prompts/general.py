# prompt templates for the general (non-code) review skill

GENERATE_PROMPT = """You are a knowledgeable assistant answering a question clearly and accurately.

Request:
{user_input}

Provide a clear, well-structured response.
"""

CRITIQUE_PROMPT = """You are a strict reviewer evaluating the quality of a draft response.

Original request:
{user_input}

Draft:
{draft}

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

REFINE_PROMPT = """You are revising a draft based on reviewer feedback.

Original request:
{user_input}

Current draft:
{draft}

Keep these strengths intact:
{strengths}

Fix these weaknesses:
{weaknesses}

Apply these suggestions:
{suggestions}

{correction_notes}

Write the improved draft only. Do not include explanations or commentary.
"""