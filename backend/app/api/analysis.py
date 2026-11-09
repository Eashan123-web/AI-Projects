import logging
from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, field_validator
from starlette.concurrency import run_in_threadpool

from app.services.suggestion_service import generate_resume_recommendations
from app.services.resume_service import extract_resume_text
from app.services.skill_service import extract_skills
from app.services.job_service import analyze_job_description
from app.services.matching_service import calculate_match
from app.services.ollama_service import generate_ai_response
from app.services.rag_service import build_resume_rag_context
from app.services.resume_improvement_service import generate_resume_improvements
from app.database.resume_repository import get_resume_by_filename
from app.database.job_repository import save_job_description
from app.database.analysis_repository import save_analysis_result
from app.database.recommendation_repository import save_recommendations

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/analysis", tags=["Resume Job Matching"],)

BASE_DIR = Path(__file__).resolve().parents[2]
UPLOAD_DIR = BASE_DIR / "uploads"

class MatchRequest(BaseModel):
    filename: str = Field(min_length=36, max_length=37)
    job_description: str = Field(min_length=30, max_length=30000)

    @field_validator("filename")
    @classmethod
    def validate_filename(cls, value):
        value = value.strip()

        if not value:
            raise ValueError("Filename cannot be empty.")

        if Path(value).name != value:
            raise ValueError("Invalid filename.")

        extension = Path(value).suffix.lower()

        if extension not in [".pdf", ".docx"]:
            raise ValueError("Only PDF and DOCX resumes are allowed.")

        filename_id = Path(value).stem

        if len(filename_id) != 32:
            raise ValueError("Invalid resume filename.")

        try:
            int(filename_id, 16)
        except ValueError:
            raise ValueError("Invalid resume filename.")

        return value

    @field_validator("job_description")
    @classmethod
    def validate_job_description(cls, value):
        value = value.strip()

        if not value:
            raise ValueError("Job description cannot be empty.")

        if len(value) < 30:
            raise ValueError("Job description must contain at least 30 characters.")

        return value

def get_resume_file(filename: str) -> Path:
    """Validate the uploaded resume filename and return its path."""

    if Path(filename).name != filename:
        raise HTTPException(status_code=400, detail="Invalid resume filename.",)

    file_path = UPLOAD_DIR / filename

    if not file_path.is_file():
        raise HTTPException(status_code=404, detail="Resume file not found. Please upload your resume again.",)

    return file_path

def generate_ai_match_analysis(resume_text, job_description, resume_skills, job_analysis, matching_analysis,
    relevant_chunks=None,):
    """Generate AI-powered resume and job matching insights."""

    prompt = f"""
You are an expert technical recruiter and resume analyst.

Analyze the candidate's resume against the provided job description.

RESUME:
{resume_text[:12000]}

JOB DESCRIPTION:
{job_description[:12000]}

RESUME SKILLS:
{resume_skills}

JOB ANALYSIS:
{job_analysis}

MATCHING ANALYSIS:
{matching_analysis}

RELEVANT RESUME CONTEXT:
{relevant_chunks or "No additional context available."}

Provide your response with the following sections:

1. Overall candidate suitability
2. Strong matching areas
3. Important missing skills
4. Experience and technical gaps
5. Practical recommendations
6. Interview preparation suggestions

Be specific and base your analysis only on the supplied information.
Do not invent candidate experience or qualifications."""

    return generate_ai_response(prompt)

@router.post("/match")
async def match_resume_with_job(request: MatchRequest):
    """Analyze a resume against a job description."""

    try:
        file_path = get_resume_file(request.filename)

        resume_text = await run_in_threadpool(extract_resume_text, str(file_path),)

        if not resume_text or not resume_text.strip():
            raise HTTPException(status_code=422, detail="Could not extract readable text from the resume.",)

        resume_skills = await run_in_threadpool(extract_skills, resume_text,)

        job_analysis = await run_in_threadpool(analyze_job_description, request.job_description,)

        job_skills = job_analysis.get("skills", [])

        matching_analysis = await run_in_threadpool(calculate_match, resume_skills, job_skills,)

        resume_record = await run_in_threadpool(get_resume_by_filename, request.filename,)

        if not resume_record:
            raise HTTPException(status_code=404, detail="Resume record not found in the database.",)

        resume_id = resume_record["resume_id"]

        # Retrieve relevant resume chunks using RAG.
        rag_analysis = {}

        try:
            rag_analysis = await run_in_threadpool(build_resume_rag_context, resume_id, request.job_description, 5,)

        except Exception:
            logger.exception("RAG context generation failed.")

            rag_analysis = {"relevant_chunks": [], "context": "", "status": "unavailable",}

        # Generate AI analysis using the retrieved RAG context.
        try:
            ai_analysis = await run_in_threadpool(generate_ai_match_analysis, resume_text, request.job_description,
                resume_skills, job_analysis, matching_analysis, rag_analysis.get("relevant_chunks", []),)

        except Exception:
            logger.exception("AI match analysis failed.")

            ai_analysis = {"message": "AI analysis is temporarily unavailable."}

        # Save job description and analysis in PostgreSQL.
        job_id = await run_in_threadpool(save_job_description, resume_id, request.job_description,)

        analysis_id = await run_in_threadpool(save_analysis_result, resume_id, job_id, matching_analysis,)

        return {
            "message": "Resume and job description analyzed successfully.", "resume_id": resume_id, "job_id": job_id,
            "analysis_id": analysis_id, "resume_filename": request.filename, "resume_skills": resume_skills,
            "job_analysis": job_analysis, "matching_analysis": matching_analysis, "rag_analysis": rag_analysis,
            "ai_analysis": ai_analysis, "database_status": "saved", "status": "success",
        }

    except HTTPException:
        raise

    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error),)

    except Exception:
        logger.exception("Resume matching failed.")

        raise HTTPException(status_code=500, detail="An unexpected error occurred during resume analysis.",)

@router.post("/recommendations")
async def get_resume_recommendations(request: MatchRequest):
    """Generate personalized recommendations for improving a resume."""

    try:
        file_path = get_resume_file(request.filename)

        resume_text = await run_in_threadpool(extract_resume_text, str(file_path),)

        if not resume_text or not resume_text.strip():
            raise HTTPException(status_code=422, detail="Could not extract readable text from the resume.",)

        resume_skills = await run_in_threadpool(extract_skills, resume_text,)

        job_analysis = await run_in_threadpool(analyze_job_description, request.job_description,)

        job_skills = job_analysis.get("skills", [])

        matching_analysis = await run_in_threadpool(calculate_match, resume_skills, job_skills,)

        resume_record = await run_in_threadpool(get_resume_by_filename, request.filename,)

        if not resume_record:
            raise HTTPException(status_code=404, detail="Resume record not found in the database.",)

        resume_id = resume_record["resume_id"]

        recommendations = await run_in_threadpool(generate_resume_recommendations, resume_skills, job_analysis,
            matching_analysis,)

        job_id = await run_in_threadpool(save_job_description, resume_id, request.job_description,)

        analysis_id = await run_in_threadpool(save_analysis_result, resume_id, job_id, matching_analysis,)

        recommendation_id = await run_in_threadpool(save_recommendations, analysis_id, recommendations,)

        return {
            "message": "Resume recommendations generated successfully.", "resume_id": resume_id, "job_id": job_id,
            "analysis_id": analysis_id, "recommendation_id": recommendation_id, "resume_skills": resume_skills,
            "job_analysis": job_analysis, "matching_analysis": matching_analysis, "recommendations": recommendations,
            "status": "success",
        }

    except HTTPException:
        raise

    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error),)

    except Exception:
        logger.exception("Resume recommendation generation failed.")

        raise HTTPException(status_code=500, detail="An unexpected error occurred while generating recommendations.",)


@router.post("/improve")
async def improve_resume(request: MatchRequest):
    """Generate AI-powered resume improvement suggestions."""

    try:
        file_path = get_resume_file(request.filename)

        resume_text = await run_in_threadpool(extract_resume_text, str(file_path),)

        if not resume_text or not resume_text.strip():
            raise HTTPException(status_code=422, detail="Could not extract readable text from the resume.",)

        resume_skills = await run_in_threadpool(extract_skills, resume_text,)

        job_analysis = await run_in_threadpool(analyze_job_description, request.job_description,)

        job_skills = job_analysis.get("skills", [])

        matching_analysis = await run_in_threadpool(calculate_match, resume_skills, job_skills,)

        resume_record = await run_in_threadpool(get_resume_by_filename, request.filename,)

        if not resume_record:
            raise HTTPException(status_code=404, detail="Resume record not found in the database.",)

        resume_id = resume_record["resume_id"]

        # Retrieve relevant resume context.
        rag_analysis = {}

        try:
            rag_analysis = await run_in_threadpool(build_resume_rag_context, resume_id, request.job_description, 5,)

        except Exception:
            logger.exception("RAG context generation failed.")

            rag_analysis = {"relevant_chunks": [], "context": "", "status": "unavailable",}

        improvements = await run_in_threadpool(generate_resume_improvements, resume_text, resume_skills, job_analysis,
            matching_analysis, rag_analysis,)

        return {
            "message": "Resume improvement suggestions generated successfully.", "resume_id": resume_id,
            "resume_filename": request.filename, "job_analysis": job_analysis,
            "match_score": matching_analysis.get("match_score"), "matching_analysis": matching_analysis,
            "rag_analysis": rag_analysis, "improvements": improvements, "status": "success",
        }

    except HTTPException:
        raise

    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error),)

    except Exception:
        logger.exception("Resume improvement generation failed.")

        raise HTTPException(status_code=500, detail="An unexpected error occurred while improving the resume.",)