
from pathlib import Path
from uuid import uuid4
from zipfile import ZipFile, BadZipFile
from fastapi import APIRouter, UploadFile, File, HTTPException

from app.services.resume_service import extract_resume_text
from app.database.resume_repository import save_resume_metadata

# Create Resume API Router
router = APIRouter(prefix="/api/resumes", tags=["Resume Upload"])

# Maximum upload size: 5 GB
MAX_FILE_SIZE = 5 * 1024 * 1024 * 1024

# Maximum uncompressed DOCX archive size: 50 GB
MAX_DOCX_UNCOMPRESSED_SIZE = 50 * 1024 * 1024 * 1024

# Project backend directory
BASE_DIR = Path(__file__).resolve().parents[2]

# Resume storage directory
UPLOAD_DIR = BASE_DIR / "uploads"

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

def validate_docx(file_path: Path):
    """Validate DOCX ZIP structure and prevent oversized archives."""

    try:
        with ZipFile(file_path, "r") as archive:

            files = archive.infolist()

            if not files:
                raise HTTPException(status_code=400, detail="DOCX file is empty.")

            # Check total uncompressed size
            total_size = sum(item.file_size for item in files)

            if total_size > MAX_DOCX_UNCOMPRESSED_SIZE:
                raise HTTPException(status_code=400, detail="DOCX document contains excessive uncompressed data.")

            # Reject suspicious compression ratios
            for item in files:

                if item.file_size > 0 and item.compress_size == 0:
                    raise HTTPException(status_code=400, detail="Invalid DOCX archive.")

                if (item.compress_size > 0 and item.file_size / item.compress_size > 100):
                    raise HTTPException(status_code=400, detail="DOCX compression ratio is too high.")

            # Required DOCX document structure
            required_files = ["[Content_Types].xml", "word/document.xml"]

            archive_names = set(archive.namelist())

            for required_file in required_files:
                if required_file not in archive_names:
                    raise HTTPException(status_code=400, detail="Invalid DOCX document structure.")

            # Check archive integrity
            corrupted_file = archive.testzip()

            if corrupted_file:
                raise HTTPException(status_code=400, detail="DOCX archive is corrupted.")

    except BadZipFile:
        raise HTTPException(status_code=400, detail="Invalid DOCX file.")

# API 1: Upload Resume

@router.post("/upload")
async def upload_resume(file: UploadFile = File(...)):

    original_filename = Path(file.filename or "").name

    if not original_filename:
        raise HTTPException(status_code=400, detail="Filename is required.")

    extension = Path(original_filename).suffix.lower()

    # Validate extension
    if extension not in [".pdf", ".docx"]:
        raise HTTPException(status_code=400, detail="Only PDF and DOCX files are allowed.")

    # Generate unique server-side filename
    unique_filename = f"{uuid4().hex}{extension}"

    file_path = UPLOAD_DIR / unique_filename

    file_size = 0
    first_chunk = b""

    try:

        # Save file using streaming
        with file_path.open("wb") as output_file:

            while True:

                chunk = await file.read(1024 * 1024)

                if not chunk:
                    break

                file_size += len(chunk)

                # Enforce upload size limit
                if file_size > MAX_FILE_SIZE:
                    raise HTTPException(status_code=413, detail="File size must not exceed 5 GB.")

                # Capture file signature
                if not first_chunk:
                    first_chunk = chunk[:8]

                output_file.write(chunk)

        # Reject empty files
        if file_size == 0:
            raise HTTPException(status_code=400, detail="Uploaded file is empty.")

        # Validate actual file format
        if extension == ".pdf":

            if not first_chunk.startswith(b"%PDF-"):
                raise HTTPException(status_code=400, detail="Invalid PDF file.")

        elif extension == ".docx":

            if not first_chunk.startswith(b"PK"):
                raise HTTPException(status_code=400, detail="Invalid DOCX file.")

            validate_docx(file_path)

        # SAVE RESUME METADATA IN POSTGRESQL

        file_type = extension.replace(".", "").upper()

        resume_record = save_resume_metadata(
            filename=unique_filename, original_filename=original_filename, file_type=file_type, file_size=file_size,
            storage_path=str(file_path)
        )

        # Successful upload response
        return {
            "message": "Resume uploaded and saved successfully!", "resume_id": resume_record["id"],
            "filename": unique_filename, "original_filename": original_filename, "file_size": file_size,
            "file_type": file_type, "database_status": "saved", "status": "success"
        }

    except HTTPException:
        if file_path.exists():
            file_path.unlink()

        raise

    except Exception:
        if file_path.exists():
            file_path.unlink()

        raise HTTPException(status_code=500, detail="Resume upload failed. Please try again.")

    finally:
        await file.close()

# API 2: Extract Resume Text

@router.get("/{filename}/text")
async def get_resume_text(filename: str):

    # Allow only filenames generated by this application
    if (len(filename) not in [36, 37] or filename[-5:] not in [".docx", ".pdf"]):
        raise HTTPException(status_code=400, detail="Invalid filename.")

    file_id = Path(filename).stem

    try:
        # Validate UUID hexadecimal format
        if len(file_id) != 32:
            raise ValueError("Invalid UUID length.")

        int(file_id, 16)

    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid filename.")

    file_path = UPLOAD_DIR / filename

    # Check whether resume exists
    if not file_path.is_file():
        raise HTTPException(status_code=404, detail="Resume not found.")

    try:

        # Extract PDF or DOCX text
        extracted_text = extract_resume_text(str(file_path))

        return {
            "filename": filename, "extracted_text": extracted_text, "character_count": len(extracted_text),
            "status": "success"
        }

    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error))

    except Exception:
        raise HTTPException(status_code=500, detail="Unable to extract resume text.")