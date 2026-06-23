import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY=os.getenv("GROQ_API_KEY")
SCORE_THRESHOLD=8.0
MAX_ITERATION=3
LOCAL_MODEL_NAME="llama3.2"
GROQ_MODEL_NAME="llama-3.1-8b-instant"
GROQ_TOOL_MODEL_NAME = "llama-3.3-70b-versatile"