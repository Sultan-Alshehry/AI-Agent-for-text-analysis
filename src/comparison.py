import json
from pathlib import Path

"""
Comparison Module
-----------------
Compares keywords and topics between multiple analyzed documents.

"""

# -------------------------------------------------------------------
# Helper functions
# -------------------------------------------------------------------


def __parse_list(value) -> list:
    # Convert value to list.
    if value is None:
        return []
    if isinstance(value, str):
        return [item.strip() for item in value.split(",")]
    if isinstance(value, list):
        result = []
        for item in value:
            if isinstance(item, dict):
                extracted = item.get("topic_name") or item.get("keyword") or str(item)
                result.append(extracted)
            else:
                result.append(str(item))
        return result
    return []


# -------------------------------------------------------------------
# Main functions
# -------------------------------------------------------------------


def load_results(filepath: str) -> dict:
    # Load saved JSON for a document.
    filename = Path(filepath).stem
    src_dir = Path(__file__).resolve().parent
    output_path = src_dir / "output" / "summary" / f"{filename}.json"

    if not output_path.exists():
        raise FileNotFoundError(
            f"No results found for '{filename}'. Analyze a document first!"
        )
    
    with open(output_path, "r", encoding="utf-8") as f:
        return json.load(f)


def compare_results(filepaths: list) -> dict:
    # Compare keywords and topics between documents.
    all_results = [load_results(filepath) for filepath in filepaths]

    all_keywords = [set(keywords.lower() for keywords in __parse_list(r.get("keywords", ""))) for r in all_results]
    all_topics = [set(topics.lower() for topics in __parse_list(r.get("topics", ""))) for r in all_results]
    common_keywords = set.intersection(*all_keywords)
    common_topics = set.intersection(*all_topics)

    per_document = []
    for i, result in enumerate(all_results):
        per_document.append({
            "file": Path(filepaths[i]).name,
            "unique_keywords": list(all_keywords[i] - common_keywords),
            "unique_topics": list(all_topics[i] - common_topics),
        })

    return {
        "common_keywords": list(common_keywords),
        "common_topics": list(common_topics),
        "per_document": per_document,
    }