import logging
from graph.builder import build_graph

logger=logging.getLogger(__name__)

def generate_mermaid()->str:
    graph=build_graph()
    mermaid_code=graph.get_graph().draw_mermaid()
    return mermaid_code

def save_mermaid(filepath: str = "graph/diagram.md") -> None:
    mermaid_code = generate_mermaid()

    # strip YAML frontmatter block if present — VS Code preview doesn't support it
    lines = mermaid_code.splitlines()
    if lines and lines[0].strip() == "---":
        end_idx = next(
            (i for i in range(1, len(lines)) if lines[i].strip() == "---"),
            None,
        )
        if end_idx is not None:
            lines = lines[end_idx + 1:]
    mermaid_code = "\n".join(lines).strip()

    content = f"```mermaid\n{mermaid_code}\n```"

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    logger.info("Mermaid diagram saved to %s", filepath)


if __name__ == "__main__":
    code = generate_mermaid()
    print(code)
    save_mermaid()