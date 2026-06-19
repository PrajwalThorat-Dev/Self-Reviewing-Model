
#phrases suggesting the user is trying to override system instruction
INJECTION_PATTERNS=[
    "ignore previous instructions",
    "ignore the above",
    "disregard your instructions",
    "you are now",
    "act as if",
    "system prompt",
    "reveal your prompt",
]

#dangerous code patterns that should never reach the user unflagged
DANGEROUS_CODE_PATTERN=[
    "eval(",
    "exec(",
    "os.system(",
    "subprocess.call(",
    "subprocess.Popen(",
    "__import__(",
    "pickle.loads(",
    "shell=True",
]