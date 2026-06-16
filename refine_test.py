import logging
logging.basicConfig(level=logging.INFO)

from nodes.refine import refine_node

dummy_state = {
    "user_input": "Explain how transformers work",
    "draft": "Transformers were invented in 2020 by OpenAI and use a recurrent neural network architecture.",
    "fact_check": {
        "is_accurate": False,
        "flagged_claims": [
            "Transformers were invented in 2020",
            "Transformers use a recurrent neural network architecture",
        ],
        "corrections": [
            "Transformers were actually invented in 2017 by Vaswani et al.",
            "Transformers use a self-attention mechanism, not a recurrent neural network architecture.",
        ],
    },
    "critique": {
        "strengths": ["Attempts a concise explanation"],
        "weaknesses": [
            "Contains factual errors.",
            "Lacks explanation of self-attention mechanism.",
        ],
        "suggestions": [
            "Correct the invention year and inventors.",
            "Explain the self-attention mechanism clearly.",
        ],
        "score": 4.0,
    },
    "score": 4.0,
    "iteration": 1,
    "max_iterations": 3,
    "final_output": None,
}

result = refine_node(dummy_state)
print(result)