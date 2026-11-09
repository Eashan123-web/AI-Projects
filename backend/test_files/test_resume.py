
import io
import zipfile

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.api import resume as resume_api

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_test_environment(tmp_path, monkeypatch):
    """Use a temporary upload directory and prevent database writes."""

    monkeypatch.setattr(resume_api, "UPLOAD_DIR", tmp_path)

    monkeypatch.setattr(resume_api, "save_resume_metadata", lambda *args, **kwargs: None,)

def create_valid_docx():
    """Create a minimal valid DOCX archive for upload testing."""

    file_bytes = io.BytesIO()

    with zipfile.ZipFile(file_bytes, "w") as archive:
        archive.writestr(
            "[Content_Types].xml",
            '<?xml version="1.0"?>'
            '<Types xmlns="http://schemas.openxmlformats.org/'
            'package/2006/content-types">'
            '</Types>',)

        archive.writestr(
            "word/document.xml",
            '<?xml version="1.0"?>'
            '<document><body><p>Test resume</p></body></document>',)

    file_bytes.seek(0)

    return file_bytes.read()

def test_upload_valid_pdf():
    """A valid PDF should upload successfully."""

    pdf_content = b"%PDF-1.4\nTest resume content"

    response = client.post(
        "/api/resumes/upload",
        files={
            "file": ("resume.pdf", pdf_content, "application/pdf",)
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "success"
    assert data["filename"].endswith(".pdf")

def test_upload_valid_docx():
    """A valid DOCX should upload successfully."""

    docx_content = create_valid_docx()

    response = client.post(
        "/api/resumes/upload",
        files={
            "file": ("resume.docx", docx_content, "application/vnd.openxmlformats-officedocument."
                "wordprocessingml.document",
            )
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "success"
    assert data["filename"].endswith(".docx")

def test_upload_invalid_file_extension():
    """TXT files should be rejected."""

    response = client.post(
        "/api/resumes/upload",
        files={
            "file": ("resume.txt", b"Some resume content", "text/plain",)
        },
    )

    assert response.status_code == 400

def test_upload_empty_file():
    """Empty files should be rejected."""

    response = client.post(
        "/api/resumes/upload",
        files={
            "file": ("resume.pdf", b"", "application/pdf",)
        },
    )

    assert response.status_code == 400

def test_upload_invalid_pdf_signature():
    """A PDF without a valid PDF signature should be rejected."""

    response = client.post(
        "/api/resumes/upload",
        files={
            "file": ("resume.pdf", b"This is not a valid PDF file", "application/pdf",)
        },
    )

    assert response.status_code == 400

def test_upload_invalid_docx():
    """A DOCX file without a valid Word document structure should be rejected."""

    response = client.post(
        "/api/resumes/upload",
        files={
            "file": ("resume.docx", b"This is not a valid DOCX archive", "application/octet-stream",)
        },
    )

    assert response.status_code == 400

def test_upload_oversized_file():
    """Files exceeding the 10 MB limit should be rejected."""

    oversized_content = b"A" * (10 * 1024 * 1024 + 1)

    response = client.post(
        "/api/resumes/upload",
        files={
            "file": ("resume.pdf", b"%PDF-1.4\n" + oversized_content, "application/pdf",)
        },
    )

    assert response.status_code == 413