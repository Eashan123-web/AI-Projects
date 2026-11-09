import logging

from fastapi import APIRouter, HTTPException, Query, Path
from starlette.concurrency import run_in_threadpool

from app.database.history_repository import (get_all_resumes, get_all_analyses, get_analysis_details,)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/history", tags=["Analysis History"],)

@router.get("/resumes")
async def list_uploaded_resumes(limit: int = Query(default=20, ge=1, le=100), offset: int = Query(default=0, ge=0),):
    """Retrieve uploaded resume history with pagination."""

    try:
        resumes = await run_in_threadpool(get_all_resumes, limit=limit, offset=offset,)

        return {
            "message": "Resume history retrieved successfully.", "total_returned": len(resumes), "limit": limit,
            "offset": offset, "resumes": resumes, "status": "success",
        }

    except Exception:
        logger.exception("Resume history retrieval failed.")

        raise HTTPException(status_code=500, detail="Unable to retrieve resume history.",)

@router.get("/analyses")
async def list_analysis_history(limit: int = Query(default=20, ge=1, le=100), offset: int = Query(default=0, ge=0),):
    """Retrieve analysis history with pagination."""

    try:
        analyses = await run_in_threadpool(get_all_analyses, limit=limit, offset=offset,)

        return {
            "message": "Analysis history retrieved successfully.", "total_returned": len(analyses), "limit": limit,
            "offset": offset, "analyses": analyses, "status": "success",
        }

    except Exception:
        logger.exception("Analysis history retrieval failed.")

        raise HTTPException(status_code=500, detail="Unable to retrieve analysis history.",)

@router.get("/analyses/{analysis_id}")
async def retrieve_analysis_details(analysis_id: int = Path(..., ge=1),):
    """Retrieve complete details of a particular analysis."""

    try:
        analysis = await run_in_threadpool(get_analysis_details, analysis_id,)

        if not analysis:
            raise HTTPException(status_code=404, detail="Analysis record not found.",)

        return {
            "message": "Analysis details retrieved successfully.", "analysis": analysis, "status": "success",
        }

    except HTTPException:
        raise

    except Exception:
        logger.exception("Analysis details retrieval failed for ID %s.", analysis_id,)

        raise HTTPException(status_code=500, detail="Unable to retrieve analysis details.",)