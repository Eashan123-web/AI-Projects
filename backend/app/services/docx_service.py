
from docx import Document
from pathlib import Path

def extract_text_from_docx(file_path: str) -> str:
    """Extract text from a DOCX resume."""

    docx_path = Path(file_path)

    if not docx_path.exists():
        raise FileNotFoundError("DOCX file not found.")

    document = Document(docx_path)

    extracted_text = []

    # Extract paragraphs
    for paragraph in document.paragraphs:
        if paragraph.text.strip():
            extracted_text.append(paragraph.text)

    # Extract tables
    for table in document.tables:
        for row in table.rows:
            row_text = [
                cell.text.strip()
                for cell in row.cells
                if cell.text.strip()
            ]

            if row_text:
                extracted_text.append(" | ".join(row_text))

    return "\n".join(extracted_text).strip()