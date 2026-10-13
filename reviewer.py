"""The reviewer: checks a draft and returns a structured verdict."""
import re
from pydantic import BaseModel, ValidationError
from ollama import chat
from config import MODEL_BIG


class Review(BaseModel):
    # problems comes BEFORE approved on purpose: the model writes JSON from top
    # to bottom, so this makes it look for problems first and decide after.
    problems: list[str]
    approved: bool


# The model only judges facts. Counting is done in Python (see code_checks),
# because small models get counts wrong but Python never does.
SYSTEM = """You check a student revision guide against research notes.
Your only job: is every fact in the guide supported by the research notes?
Ignore formatting, length and the number of questions. Those are checked elsewhere.
List each unsupported fact as one short sentence in "problems".
Only list real problems. If there are none, leave "problems" empty and set
"approved" to true."""


def section(draft: str, heading: str) -> list[str]:
    """Return the non-empty lines under a '## heading', up to the next '##'."""
    lines, inside = [], False
    for line in draft.splitlines():
        if line.startswith("## "):
            inside = line[3:].strip().lower() == heading.lower()
        elif inside and line.strip():
            lines.append(line.strip())
    return lines


def code_checks(draft: str) -> list[str]:
    """Rules that plain Python can check reliably. No model needed."""
    problems = []

    # Every bullet under "Key points" must end with [source] (a final "." is fine)
    bullets = [l for l in section(draft, "Key points") if l[:1] in "-*•"]
    if not bullets:
        problems.append('Missing the "## Key points" bullet list.')
    for number, bullet in enumerate(bullets, start=1):
        if not re.search(r"\]\.?$", bullet):
            problems.append(f"Key point {number} does not end with a [source].")

    # Exactly 3 numbered questions, like "1. ...", "2. ...", "3. ..."
    questions = [l for l in section(draft, "Self-test questions") if re.match(r"\d+\.", l)]
    if len(questions) != 3:
        problems.append(f"Need exactly 3 numbered self-test questions, found {len(questions)}.")

    words = len(draft.split())
    if words > 400:
        problems.append(f"Too long: {words} words, keep it under 400.")
    return problems


def review_draft(draft: str, notes: str) -> Review:
    problems = code_checks(draft)

    response = chat(
        model=MODEL_BIG, think=False,
        format=Review.model_json_schema(),          # forces JSON in this shape
        # temperature 0 = same answer every time; num_predict caps the reply
        # length so the model can't ramble until the JSON breaks
        options={"temperature": 0, "num_predict": 400},
        messages=[{"role": "system", "content": SYSTEM},
                  {"role": "user", "content": f"Research notes:\n{notes}\n\nDraft:\n{draft}"}],
    )
    try:
        verdict = Review.model_validate_json(response.message.content)
    except ValidationError:
        verdict = Review(approved=False, problems=["Reviewer reply was not valid JSON."])

    # If the model approved, ignore any stray notes it left in "problems"
    if not verdict.approved:
        problems += verdict.problems or ["Reviewer rejected the draft without a reason."]
    return Review(approved=not problems, problems=problems)
