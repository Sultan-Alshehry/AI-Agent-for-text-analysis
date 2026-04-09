from pathlib import Path

DEFAULT_SUMMARY_PATH = (
    Path(__file__).resolve().parent / "output" / "summary" / "summary.json"
)
API_KEY = ""
KEYBERT_INSTALLED = False
ANALYSIS_MODE = ""

# initial values only, later will be assigned in a function based
# on the file word count

MAX_SUMMARY = 60
MAX_KEYWORDS = 5
MAX_TOPICS = 3

JSON_FORMAT = {
    "summary": "summary here",
    "keywords": "keywords here",
    "topics": "topics here",
}

AI_MODEL = "gemini-3-flash-preview"
#AI_MODEL = "gemini-3.1-flash-lite-preview"