
from pathlib import Path
from fastapi import APIRouter, HTTPException

from app.services.resume_service import extract_resume_text
from app.services.skill_service import extract_skills

# Create API router
router = APIRouter(prefix="/api/skills", tags=["Skill Extraction"])

BASE_DIR = Path(__file__).resolve().parents[2]
UPLOAD_DIR = BASE_DIR / "uploads"

@router.get("/extract/{filename}")
async def extract_resume_skills(filename: str):

    if Path(filename).name != filename:
        raise HTTPException(status_code=400, detail="Invalid filename.")

    file_path = UPLOAD_DIR / filename

    if not file_path.is_file():
        raise HTTPException(status_code=404, detail="Resume not found.")

    try:
        resume_text = extract_resume_text(str(file_path))

        skills = extract_skills(resume_text)

        total_skills = sum(
            len(category_skills)
            for category_skills in skills.values()
        )

        return {
            "filename": filename, "skills": skills, "total_skills": total_skills, "status": "success"
        }

    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error))

    except Exception as error:
        print("Skill extraction error:", error)

        raise HTTPException(status_code=500, detail="Unable to extract resume skills.")