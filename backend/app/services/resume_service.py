
from pathlib import Path

from app.services.pdf_service import extract_text_from_pdf
from app.services.docx_service import extract_text_from_docx

def extract_resume_text(file_path: str) -> str:
    """Identify resume format and extract its text."""

    extension = Path(file_path).suffix.lower()

    if extension == ".pdf":
        text = extract_text_from_pdf(file_path)

    elif extension == ".docx":
        text = extract_text_from_docx(file_path)

    else:
        raise ValueError("Unsupported resume format.")

    if not text:
        raise ValueError("No readable text found in the resume.")

    return text