"""The crew as a graph: nodes are agents, edges are who goes next."""
from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from config import MAX_DRAFTS
from researcher import research
from writer import write_guide
from reviewer import review_draft


# The state is the shared notebook every agent reads and writes.
class CrewState(TypedDict):
    topic: str
    notes: str       # researcher's findings
    draft: str       # writer's latest guide
    feedback: str    # "APPROVED" or the reviewer's problems
    drafts: int      # how many drafts the writer has made


# ---------- Real agents ----------
def researcher(state: CrewState) -> dict:
    notes, used = research(state["topic"])
    if not used:
        print("    (warning: the researcher used no tools, so notes may be made up)")
    return {"notes": notes}


def writer(state: CrewState) -> dict:
    draft = write_guide(state["topic"], state["notes"], state["draft"], state["feedback"])
    return {"draft": draft, "drafts": state["drafts"] + 1}


def reviewer(state: CrewState) -> dict:
    review = review_draft(state["draft"], state["notes"])
    if review.approved:
        return {"feedback": "APPROVED"}
    return {"feedback": "\n".join(f"- {p}" for p in review.problems)}


# ---------- Where to go after the reviewer ----------
def after_review(state: CrewState) -> str:
    if state["feedback"] == "APPROVED" or state["drafts"] >= MAX_DRAFTS:
        return "done"
    return "revise"


graph = StateGraph(CrewState)
graph.add_node("researcher", researcher)
graph.add_node("writer", writer)
graph.add_node("reviewer", reviewer)
graph.add_edge(START, "researcher")
graph.add_edge("researcher", "writer")
graph.add_edge("writer", "reviewer")
graph.add_conditional_edges("reviewer", after_review, {"revise": "writer", "done": END})
app = graph.compile()