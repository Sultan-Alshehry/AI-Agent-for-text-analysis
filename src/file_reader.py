from pathlib import Path


# read a .txt file
def __read_txt(path: Path) -> str:
    return path.read_text(encoding="utf-8")


# read a file and return the text content
def read_file(file_path: str) -> str:

    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    file_type = path.suffix.lower()

    if file_type == ".txt":
        return __read_txt(path)
    else:
        raise ValueError(f"Unsupported file type: {file_type}")
