
from pathlib import Path
from PyPDF2 import PdfReader
import re


"""
File Reader Module
------------------
Handles file input operations with support for multiple formats:
- Plain text (.txt) files using UTF-8 encoding
- PDF files using PyPDF2 for text extraction

Validates file existence and format.
Provides both file validation and content extraction.
"""


def validate_and_read_file(file_path: str) -> tuple[bool, str]:
    # Validate and attempt to read a file in one operation.
    try:
        path = Path(file_path)
        if not path.exists():
            return False, f"File not found: {file_path}"
        
        if path.suffix.lower() not in [".txt", ".pdf"]:
            return False, f"Unsupported file type: {path.suffix}. Please use .txt or .pdf"
        
        content = read_file(file_path)
        
        if not content.strip():
            return False, "File is empty or contains no readable text"
        
        return True, content
    
    except Exception as e:
        return False, f"Error reading file: {str(e)}"


def validate_file(file_path: str) -> bool:
    path = Path(file_path)
    if not path.exists():
        return False
    return path.suffix.lower() in (".txt", ".pdf")


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


def __read_txt(path: Path) -> str:
    return path.read_text(encoding="utf-8")


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

    text = "\n".join(pages)
    text = re.sub(r"-\n(?=[a-z])", "", text)
    text = re.sub(r"(?<=[a-z])\n(?=[a-z])", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text
