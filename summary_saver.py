import json
import state
from pathlib import Path
from typing import Any, Dict, Optional, Union

from analysis_formatter import normalize_keyword_labels, normalize_topic_labels, stringify_analysis_items
from file_reader import read_file


"""
Summary Saver Module
--------------------
Handles saving analysis results to files in JSON or text format.

Supports formatted output with normalized labels and directory creation.
"""


# -------------------------------------------------------------------
# Helper functions
# -------------------------------------------------------------------


def _ensure_parent_dir(path: Path) -> None:
    # Ensure the parent directory of the given path exists.
    parent = path.parent
    if not parent.exists():
        parent.mkdir(parents=True, exist_ok=True)


# -------------------------------------------------------------------
# Main save function
# -------------------------------------------------------------------


def save_summary(
    summary: Dict[str, Any],
    output_path: Optional[Union[str, Path]] = None,
    *,
    indent: int = 2,
    format: str = "json",
) -> Path:
    """Save analysis summary to a file in JSON or text format.
    
    Args:
        summary: The analysis result dictionary
        output_path: Path to save the file (defaults to state.DEFAULT_SUMMARY_PATH)
        indent: JSON indentation level
        format: Output format ('json' or 'txt')
    
    Returns:
        Path to the saved file
    """
    path = Path(output_path) if output_path is not None else state.DEFAULT_SUMMARY_PATH
    _ensure_parent_dir(path)

    with path.open("w", encoding="utf-8") as f:
        if format == "txt":
            summary_text = summary.get("summary", "")
            if isinstance(summary_text, str) and summary_text.strip():
                f.write(f"Summary: {summary_text.strip()}\n\n")

            source_text = None
            source_file = summary.get("source_file")
            mode = summary.get("mode")
            if isinstance(source_file, str) and source_file.strip():
                try:
                    source_text = read_file(source_file)
                except Exception:
                    source_text = None

            keyword_labels = normalize_keyword_labels(summary.get("keywords", []), source_text=source_text, mode=mode)
            keywords_text = ", ".join(keyword_labels) if keyword_labels else stringify_analysis_items(summary.get("keywords", []), source_text=source_text, mode=mode)
            topic_labels = normalize_topic_labels(summary.get("topics", []), mode=mode)
            topics_text = "\n".join(f"- {label}" for label in topic_labels) if topic_labels else "No topics found"
            f.write(f"Keywords: {keywords_text}\n\n")
            f.write(f"Topics: {topics_text}\n")
        else:  
            json.dump(summary, f, indent=indent, ensure_ascii=False)

    return path