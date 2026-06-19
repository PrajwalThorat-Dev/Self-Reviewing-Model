from guardrails.rules import INJECTION_PATTERNS

def check_injection(user_input: str)-> bool:
    #return true if the input looks like a prompt injection attemp
    text=user_input.lower()
    return any(pattern in text for pattern in INJECTION_PATTERNS)

def check_input(user_input: str)->dict:
    # runs all input-side checks, returns a single verdict
    if check_injection(user_input):
        return{
            "blocked":True,
            "block_reason":"Input appears to contain a prompt injection attempt.",
        }
    
    return{
        "blocked":False,
        "block_reason":"None",
    }