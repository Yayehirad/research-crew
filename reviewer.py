"""The reviewer: checks a draft and returns a structured verdict."""
from pydantic import BaseModel, ValidationError
from ollama import chat
from config import MODEL_BIG


class Review(BaseModel):
    approved: bool
    problems: list[str]


SYSTEM = """You review student revision guides. Be strict but fair.
Approve only if ALL of these are true:
- every key point ends with a [source] in square brackets
- every fact is supported by the research notes
- there are exactly 3 self-test questions
- the guide is clear and under 400 words
If anything fails, set approved to false and list each problem in one short sentence."""


def code_checks(draft: str) -> list[str]:
    """Rules that plain Python can check reliably. No model needed."""
    problems = []
    if "## Self-test questions" not in draft:
        problems.append('Missing the "## Self-test questions" heading.')
    if "[" not in draft:
        problems.append("No sources in square brackets.")
    if len(draft.split()) > 450:
        problems.append("Too long: keep it under 400 words.")
    return problems


def review_draft(draft: str, notes: str) -> Review:
    problems = code_checks(draft)

    response = chat(
        model=MODEL_BIG, think=False,
        format=Review.model_json_schema(),          # forces JSON in this shape
        options={"temperature": 0},
        messages=[{"role": "system", "content": SYSTEM},
                  {"role": "user", "content": f"Research notes:\n{notes}\n\nDraft:\n{draft}"}],
    )
    try:
        verdict = Review.model_validate_json(response.message.content)
    except ValidationError:
        verdict = Review(approved=False, problems=["Reviewer reply was not valid JSON."])

    problems += verdict.problems
    return Review(approved=verdict.approved and not problems, problems=problems)