import ast
import subprocess
import sys
import tempfile
from pathlib import Path
from langchain_core.tools import tool 

def check_syntax(code: str)-> dict:
    # determistic- called directly by the node, not by the LLM
    try:
        ast.parse(code)
        return{
            "is_valid":True,
            "errors":[],
        }
    except SyntaxError as e:
        return{
            "is_valid":False,
            "errors":[f"Syntax error at line {e.lineno}: {e.msg}"],
        }
    
@tool
def run_ruff(code: str)-> str:
    """Run the ruff linter on Python code to check for undefined names, unused imports,
    unused variables, and style violations. Use this when you want to verify the code
    more rigorously before finalizing your critique."""
    # writing code on temp file since ruff operates on files, not raw strings
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(code)
        temp_path=f.name

    try:
        result=subprocess.run(
            [sys.executable, "-m", "ruff", "check", temp_path, "--quiet"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        output=result.stdout.strip()
        return output if output else "No issues found by ruff."
    finally:
        Path(temp_path).unlink(missing_ok=True)