"""Tools the researcher can ask for. Docstrings matter: the model reads them."""
from ddgs import DDGS
from notes_index import search_index


def search_notes(query: str) -> str:
    """Search the student's own lecture notes (PDFs). Use this first.

    Args:
      query: What to look for, in a few words, for example "context window"
    """
    hits = search_index(query, k=4)
    if not hits:
        return "No matching notes found. The notes index may be empty."
    return "\n\n".join(f"[{h['file']}, page {h['page']}]\n{h['text']}" for h in hits)


def web_search(query: str) -> str:
    """Search the web. Use this when the notes don't cover something.

    Args:
      query: A short web search query, for example "what is ReAct prompting"
    """
    try:
        results = DDGS().text(query, max_results=5)
    except Exception as error:
        return f"Web search failed: {error}"
    if not results:
        return "No web results."
    return "\n\n".join(f"[{r['href']}]\n{r['title']}: {r['body']}" for r in results)


TOOLS = {"search_notes": search_notes, "web_search": web_search}