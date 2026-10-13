"""Settings for the whole crew. Change things here, not inside the other files."""
from pathlib import Path

# Models (must match the names in `ollama list`)
MODEL_BIG = "qwen3.5:9b"         # researcher and reviewer: needs careful reasoning
MODEL_FAST = "qwen3.5:4b"        # writer: lots of text, speed matters more
EMBED_MODEL = "nomic-embed-text" # turns text into numbers for search

# Where your lecture PDFs are, and where finished guides are saved.
# Change these two lines if your folders are somewhere else.
DOCS_DIR = Path.home() / "OneDrive" / "AI_Agent_Learning" / "Agent_Documents"
GUIDES_DIR = Path.home() / "OneDrive" / "AI_Agent_Learning" / "Revision_Guides"

# Folders inside this project (both are in .gitignore)
PROJECT_DIR = Path(__file__).parent
DB_DIR = PROJECT_DIR / "db"      # the search index of your PDFs
LOG_DIR = PROJECT_DIR / "logs"   # trace of every run

# Limits that keep the crew from running forever
MAX_DRAFTS = 3          # writer gets at most 3 attempts
MAX_RESEARCH_STEPS = 6  # researcher gets at most 6 rounds of tool calls