"""The crew as a graph: nodes are agents, edges are who goes next."""
from typing import TypedDict
from langgraph.graph import StateGraph, START, END


# The state is the shared notebook every agent reads and writes.
class CrewState(TypedDict):
    topic: str
    notes: str       # researcher's findings
    draft: str       # writer's latest guide
    feedback: str    # "APPROVED" or the reviewer's problems
    drafts: int      # how many drafts the writer has made


# ---------- Fake agents for now ----------
def researcher(state: CrewState) -> dict:
    return {"notes": f"(fake notes about {state['topic']})"}


def writer(state: CrewState) -> dict:
    n = state["drafts"] + 1
    return {"draft": f"(fake draft #{n})", "drafts": n}


def reviewer(state: CrewState) -> dict:
    # Pretend: reject the first draft, approve the second
    if state["drafts"] >= 2:
        return {"feedback": "APPROVED"}
    return {"feedback": "Add a worked example."}


# ---------- Where to go after the reviewer ----------
def after_review(state: CrewState) -> str:
    if state["feedback"] == "APPROVED" or state["drafts"] >= 3:
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