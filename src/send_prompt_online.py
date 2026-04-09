
from google import genai
import json
import re
import state

"""
AI Analysis Module
------------------
Handles communication with AI services for text analysis:
- Gemini (Google's generative AI): Full analysis (summary, keywords, topics)
- KeyBERT: Keyword extraction using transformer models

Supports fallback between modes and format handling for both services.
"""

try:
    from keybert_analyzer import get_keybert_keywords
except ImportError:
    from keybert_analyzer import get_keybert_keywords


def get_output(message):
    # Send text to Gemini API for analysis and return response.
    client = genai.Client(api_key=state.API_KEY)
    response = client.models.generate_content(
        model=state.AI_MODEL,
        contents="Your task is to create keywords, topics, "
        + "and a summary for the provided text. "
        + f"Maximum number of words in the summary is {state.MAX_SUMMARY}. "
        + f"Maximum number of keywords is {state.MAX_KEYWORDS}. "
        + f"Maximum number of topics is {state.MAX_TOPICS}. "
        + f"Only respond with a json object of this format: {state.JSON_FORMAT}. "
        + f"Here are the contents that you need to read: {message}",
    )
    return response


def get_output_text(output):
    # Extract and clean JSON text from Gemini response.
    output = output.candidates[0].content.parts[0].text
    cleaned = re.sub(r"^```json\s*|```$", "", output.strip(), 0, re.MULTILINE)
    return cleaned

# Analyze text with either GenAI or KeyBERT.
#   mode options:
#   genai: use AI model for everything (summary, keywords, topics)
#   keybert: use KeyBERT for keywords only (no summary or topics)
def analyze_text(message, mode="genai", top_n_keywords=None):
    if top_n_keywords is None:
        top_n_keywords = state.MAX_KEYWORDS

    result = {
        "summary": "",
        "topics": [],
        "ai_keywords": [],
        "keybert_keywords": [],
        "keywords": [],
        "token_count": None,
    }

    if mode == "genai":
        response = get_output(message)
        parsed = json.loads(get_output_text(response))
        result["summary"] = parsed.get("summary", "")
        result["ai_keywords"] = parsed.get("keywords", [])
        result["topics"] = parsed.get("topics", [])
        result["token_count"] = getattr(
            getattr(response, "usage_metadata", None), "total_token_count", None
        )
        result["keywords"] = result["ai_keywords"]

    elif mode == "keybert":
        result["keybert_keywords"] = get_keybert_keywords(
            message, top_n=top_n_keywords
        )
        result["keywords"] = result["keybert_keywords"]

    else:
        raise ValueError("Invalid mode for analyze_text: choose 'genai' or 'keybert'.")

    return result