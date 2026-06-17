import logging
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from graph.builder import build_graph

logger=logging.getLogger(__name__)

def generate_mermaid()->str:
    graph=build_graph()
    mermaid_code=graph.get_graph().draw_mermaid()
    return mermaid_code

def save_mermaid(filepath: str = "graph/diagram.md") -> None:
    mermaid_code = generate_mermaid()

    lines = mermaid_code.splitlines()
    if lines and lines[0].strip() == "---":
        end_idx = next(
            (i for i in range(1, len(lines)) if lines[i].strip() == "---"),
            None,
        )
        if end_idx is not None:
            lines = lines[end_idx + 1:]
    mermaid_code = "\n".join(lines).strip()

    output_path = Path(filepath)
    if not output_path.is_absolute():
        output_path = ROOT / output_path
    output_path.parent.mkdir(parents=True, exist_ok=True)

    print("WRITING TO:", output_path.resolve())   # temp debug
    print("FILE EXISTS AFTER MKDIR:", output_path.parent.exists())   # temp debug

    content = f"```mermaid\n{mermaid_code}\n```"

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)

    print("WRITE COMPLETE")   # temp debug
    logger.info("Mermaid diagram saved to %s", output_path)


if __name__ == "__main__":
    code = generate_mermaid()
    print(code)
    print("ABOUT TO SAVE")   # temp debug
    save_mermaid()