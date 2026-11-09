
from psycopg.types.json import Jsonb
from app.database.db import get_connection

def save_analysis_result(resume_id: int, job_id: int, match_score: float, matching_analysis: dict):
    query = """
        INSERT INTO analysis_results (resume_id, job_id, match_score, matching_analysis)
        VALUES (%s, %s, %s, %s)
        RETURNING id, resume_id, job_id, match_score, matching_analysis, created_at;
    """

    with get_connection() as connection:
        result = connection.execute(query,(resume_id, job_id, match_score, Jsonb(matching_analysis))).fetchone()

    return {
        "id": result[0], "resume_id": result[1], "job_id": result[2], "match_score": float(result[3]), 
        "matching_analysis": result[4], "created_at": result[5]
    }

def get_analysis_result(analysis_id: int):
    query = """
        SELECT id, resume_id, job_id, match_score, matching_analysis, created_at FROM analysis_results WHERE id = %s;
    """

    with get_connection() as connection:
        result = connection.execute(query, (analysis_id,)).fetchone()

    if not result:
        return None

    return {
        "id": result[0], "resume_id": result[1], "job_id": result[2], "match_score": float(result[3]),
        "matching_analysis": result[4], "created_at": result[5]
    }