import logging
from graph.builder import build_graph
from config.settings import MAX_ITERATION

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

logger=logging.getLogger(__name__)

def run(user_input: str, skill: str="general"):
    graph=build_graph()

    initial_state = {
        "user_input": user_input,
        "skill": skill,
        "draft": "",
        "fact_check": None,
        "critique": None,
        "score": 0.0,
        "iteration": 0,
        "max_iterations": MAX_ITERATION,
        "final_output": None,
    }

    final_state=graph.invoke(initial_state)

    logger.info("Run complete. Final score: %s", final_state["score"])

    print(final_state["final_output"])


if __name__=="__main__":
    run(
        "Write a Python function to check if a number is prime",
        skill="code",
        )