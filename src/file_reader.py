from pathlib import Path

# read a file and return the text content
def read_file(file_path: str) -> str:
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    file_type = path.suffix.lower()

    if file_type == ".txt":
        return __read_txt(path)

    if file_type == ".pdf":
        return __read_pdf(path)

    raise ValueError(f"Unsupported file type: {file_type}")

# read a .txt file
def __read_txt(path: Path) -> str:
    return path.read_text(encoding="utf-8")

# read a .pdf file using PyPDF2
def __read_pdf(path: Path) -> str:
    try:
        from PyPDF2 import PdfReader
    except ImportError as exc:
        raise ImportError(
            "PyPDF2 is not installed. Install with `pip install PyPDF2` to read PDF files."
        ) from exc

    reader = PdfReader(path)
    pages = []

    for page in reader.pages:
        page_text = page.extract_text() or ""
        pages.append(page_text)

    return "\n".join(pages)
