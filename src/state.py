from pathlib import Path


"""
State Module
------------
Global state variables for the AI text analysis application.

Contains configuration constants, API keys, and runtime state.
"""


# -------------------------------------------------------------------
# File paths
# -------------------------------------------------------------------

DEFAULT_SUMMARY_PATH = (
    Path(__file__).resolve().parent / "output" / "summary" / "summary.json"
)

DEFAULT_COMPARISON_PATH = (
    Path(__file__).resolve().parent / "output" / "comparison"
)

# -------------------------------------------------------------------
# Runtime state
# -------------------------------------------------------------------

API_KEY = ""
KEYBERT_INSTALLED = False
ANALYSIS_MODE = ""


# -------------------------------------------------------------------
# Analysis limits
# -------------------------------------------------------------------

# Initial values only, later will be assigned in a function based
# on the file word count
MAX_SUMMARY = 60
MAX_KEYWORDS = 5
MAX_TOPICS = 3


# -------------------------------------------------------------------
# AI configuration
# -------------------------------------------------------------------

JSON_FORMAT = {
    "summary": "summary here",
    "keywords": "keywords here",
    "topics": "topics here",
}

AI_MODEL = "gemini-3-flash-preview"
# AI_MODEL = "gemini-3.1-flash-lite-preview"