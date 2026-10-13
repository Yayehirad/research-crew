"""Run the research crew:  python main.py "your topic" """
import json
import sys
import time
from datetime import datetime
from config import GUIDES_DIR, LOG_DIR
from graph import app

sys.stdout.reconfigure(encoding="utf-8")   # so symbols from the web print safely


def log(entry: dict) -> None:
    """Append one JSON line to logs/trace.jsonl."""
    LOG_DIR.mkdir(exist_ok=True)
    entry["time"] = datetime.now().isoformat(timespec="seconds")
    with open(LOG_DIR / "trace.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def main() -> None:
    topic = " ".join(sys.argv[1:]) or "the agent loop"
    state = {"topic": topic, "notes": "", "draft": "", "feedback": "", "drafts": 0}
    print(f"Research crew starting on: {topic}\n")
    started = time.time()

    for step in app.stream(state):
        for node, update in step.items():
            state.update(update)
            log({"topic": topic, "node": node, "update": update})
            if node == "researcher":
                print(f"[researcher] gathered {len(state['notes'].splitlines())} lines of notes")
            elif node == "writer":
                print(f"[writer]     draft #{state['drafts']} ({len(state['draft'].split())} words)")
            elif node == "reviewer":
                if state["feedback"] == "APPROVED":
                    print("[reviewer]   approved")
                else:
                    print("[reviewer]   sent it back:\n" + state["feedback"])

    GUIDES_DIR.mkdir(parents=True, exist_ok=True)
    safe_name = "".join(c if c.isalnum() else "_" for c in topic).strip("_").lower()
    path = GUIDES_DIR / f"{safe_name}.md"
    path.write_text(state["draft"], encoding="utf-8")

    status = "approved" if state["feedback"] == "APPROVED" else "not approved, saved the last draft"
    print(f"\nDone in {time.time() - started:.0f}s ({status}).")
    print(f"Saved to {path}")


if __name__ == "__main__":
    main()