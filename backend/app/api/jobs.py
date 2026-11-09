
import logging

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, field_validator
from starlette.concurrency import run_in_threadpool

from app.services.job_service import analyze_job_description


logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/jobs",
    tags=["Job Description Analysis"],
)


class JobDescriptionRequest(BaseModel):
    job_description: str = Field(
        min_length=30,
        max_length=30000,
    )

    @field_validator("job_description")
    @classmethod
    def validate_job_description(cls, value):
        value = value.strip()

        if not value:
            raise ValueError("Job description cannot be empty.")

        if len(value) < 30:
            raise ValueError(
                "Job description must contain at least 30 characters."
            )

        if len(value) > 30000:
            raise ValueError(
                "Job description cannot exceed 30000 characters."
            )

        return value


@router.post("/analyze")
async def analyze_job(request: JobDescriptionRequest):
    """
    Analyze a job description and extract required skills.
    """

    try:
        result = await run_in_threadpool(
            analyze_job_description,
            request.job_description,
        )

        return {
            "message": "Job description analyzed successfully.",
            "job_description_length": len(request.job_description),
            "analysis": result,
            "status": "success",
        }

    except ValueError as error:
        raise HTTPException(
            status_code=422,
            detail=str(error),
        )

    except Exception:
        logger.exception("Job description analysis failed.")

        raise HTTPException(
            status_code=500,
            detail="Unable to analyze job description.",
        )
