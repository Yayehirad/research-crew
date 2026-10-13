"""The writer: turns research notes into a revision guide."""
from ollama import chat
from config import MODEL_FAST

SYSTEM = """You write short revision guides for students, in Markdown.
Use exactly this structure:
# <topic>
## Key points
5 to 8 bullet points. Keep the [source] at the end of each one.
## Self-test questions
Exactly 3 numbered questions.
Only use facts from the notes. Do not add sources that are not in the notes."""


def write_guide(topic: str, notes: str, draft: str = "", feedback: str = "") -> str:
    request = f"Topic: {topic}\n\nResearch notes:\n{notes}"
    if feedback:   # this is a rewrite: show the old draft and what to fix
        request += f"\n\nYour previous draft:\n{draft}\n\nFix these problems:\n{feedback}"
    response = chat(model=MODEL_FAST, think=False,
                    messages=[{"role": "system", "content": SYSTEM},
                              {"role": "user", "content": request}])
    return response.message.content