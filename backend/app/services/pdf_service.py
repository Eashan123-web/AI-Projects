
import fitz
from pathlib import Path

def extract_text_from_pdf(file_path: str) -> str:
    """Extract text from a PDF resume."""

    pdf_path = Path(file_path)

    if not pdf_path.exists():
        raise FileNotFoundError("PDF file not found.")

    extracted_text = []

    with fitz.open(pdf_path) as document:

        for page in document:
            page_text = page.get_text("text")
            extracted_text.append(page_text)

    return "\n".join(extracted_text).strip()