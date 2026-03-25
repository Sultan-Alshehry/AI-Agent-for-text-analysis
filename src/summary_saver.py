import json
import state
from pathlib import Path
from typing import Any, Dict, Optional, Union


def _ensure_parent_dir(path: Path) -> None:

    parent = path.parent
    if not parent.exists():
        parent.mkdir(parents=True, exist_ok=True)


def save_summary(
    summary: Dict[str, Any],
    output_path: Optional[Union[str, Path]] = None,
    *,
    indent: int = 2,
) -> Path:

    path = Path(output_path) if output_path is not None else state.DEFAULT_SUMMARY_PATH
    _ensure_parent_dir(path)

    with path.open("w", encoding="utf-8") as f:
        json.dump(summary, f, indent=indent, ensure_ascii=False)
        f.write("\n")

    return path
