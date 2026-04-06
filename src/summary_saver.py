import json
import state
from pathlib import Path
from typing import Any, Dict, Optional, Union

from analysis_formatter import normalize_keyword_labels, normalize_topic_labels, stringify_analysis_items


def _ensure_parent_dir(path: Path) -> None:

    parent = path.parent
    if not parent.exists():
        parent.mkdir(parents=True, exist_ok=True)


def save_summary(
    summary: Dict[str, Any],
    output_path: Optional[Union[str, Path]] = None,
    *,
    indent: int = 2,
    format: str = "json",
) -> Path:

    path = Path(output_path) if output_path is not None else state.DEFAULT_SUMMARY_PATH
    _ensure_parent_dir(path)

    with path.open("w", encoding="utf-8") as f:
        if format == "txt":
            summary_text = summary.get("summary", "")
            if isinstance(summary_text, str) and summary_text.strip():
                f.write(f"Summary: {summary_text.strip()}\n\n")

            keyword_labels = normalize_keyword_labels(summary.get("keywords", []))
            keywords_text = ", ".join(keyword_labels) if keyword_labels else stringify_analysis_items(summary.get("keywords", []))
            topic_labels = normalize_topic_labels(summary.get("topics", []))
            topics_text = "\n".join(f"- {label}" for label in topic_labels) if topic_labels else "No topics found"
            f.write(f"Keywords: {keywords_text}\n\n")
            f.write(f"Topics: {topics_text}\n")
        else:  
            json.dump(summary, f, indent=indent, ensure_ascii=False)
            f.write("\n")

    return path