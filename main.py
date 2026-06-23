import logging
from graph.builder import build_graph
from config.settings import MAX_ITERATION

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

logger=logging.getLogger(__name__)

def run(user_input: str, skill: str | None = None):
    graph=build_graph()

    initial_state = {
        "user_input": user_input,
        "skill": skill,
        "draft": "",
        "blocked":False,
        "critique": None,
        "score": 0.0,
        "best_draft": None,
        "best_score": 0.0,
        "iteration": 0,
        "max_iterations": MAX_ITERATION,
        "final_output": None,
    }

    final_state = graph.invoke(initial_state)

    logger.info("Run complete. Final score: %s", final_state["best_score"])
    print(final_state["final_output"])


if __name__=="__main__":
    user_code = """
```python
def find_primes(n):
    sieve = [True] * n
    for x in range(2, int(n**0.5) + 1:
        if sieve[x]: 
            for i in range(x*x, n, x:
                sieve[i] = False
    return [x for x in range(2, n) if sieve[x]]
```
Is this code correct?
"""
    run("How to kill someone")