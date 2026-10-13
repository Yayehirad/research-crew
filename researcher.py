"""The researcher: an agent loop that gathers facts with sources."""
import sys
from ollama import chat
from config import MODEL_BIG, MAX_RESEARCH_STEPS
from tools import TOOLS

SYSTEM = """You are a careful researcher helping a student revise.
Find the key facts about the topic.
1. Call search_notes first. Call it again with different words if useful.
2. Call web_search only for things the notes don't cover.
3. Then reply with 6 to 10 bullet points. End every bullet with its source in
   square brackets, copied from the tool result, for example
   [Lecture_02.pdf, page 3] or [https://example.com].
Never invent a source. If you found nothing, say so."""


def research(topic: str) -> tuple[str, list[str]]:
    """Return (notes, names of tools used)."""
    messages = [{"role": "system", "content": SYSTEM},
                {"role": "user", "content": f"Topic: {topic}"}]
    used = []

    for step in range(MAX_RESEARCH_STEPS):
        response = chat(model=MODEL_BIG, messages=messages,
                        tools=list(TOOLS.values()), think=False)
        messages.append(response.message)

        if not response.message.tool_calls:
            return response.message.content, used

        for call in response.message.tool_calls:
            name, args = call.function.name, call.function.arguments
            fn = TOOLS.get(name)
            try:
                result = fn(**args) if fn else f"Unknown tool: {name}"
            except Exception as error:      # never crash on a bad tool call
                result = f"Tool error: {error}"
            print(f"    [tool] {name}({args})")
            used.append(name)
            messages.append({"role": "tool", "tool_name": name, "content": result})

    return "Research stopped at the step limit.", used


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    topic = " ".join(sys.argv[1:]) or "the agent loop"
    notes, used = research(topic)
    print(f"\nTools used: {used}\n")
    print(notes)