
from app.database.db import get_connection
from app.database.recommendation_repository import get_recommendations

def get_all_resumes(limit: int = 20, offset: int = 0):

    query = """
        SELECT id, filename, original_filename, file_type, file_size, created_at FROM resumes
        ORDER BY created_at DESC, id DESC LIMIT %s OFFSET %s;
    """

    with get_connection() as connection:
        results = connection.execute(query, (limit, offset)).fetchall()

    return [
        {
            "id": row[0], "filename": row[1], "original_filename": row[2], "file_type": row[3], "file_size": row[4],
            "created_at": row[5]
        }
        for row in results
    ]


def get_all_analyses(limit: int = 20, offset: int = 0):

    query = """
        SELECT a.id, a.resume_id, r.original_filename, a.job_id, j.title, a.match_score, a.created_at
        FROM analysis_results a INNER JOIN resumes r ON a.resume_id = r.id INNER JOIN job_descriptions j
            ON a.job_id = j.id ORDER BY a.created_at DESC, a.id DESC LIMIT %s OFFSET %s;"""

    with get_connection() as connection:
        results = connection.execute(query, (limit, offset)).fetchall()

    return [
        {
            "analysis_id": row[0], "resume_id": row[1], "resume_filename": row[2], "job_id": row[3],
            "job_title": row[4], "match_score": float(row[5]), "created_at": row[6]
        }
        for row in results
    ]


def get_analysis_details(analysis_id: int):

    query = """
        SELECT a.id, a.resume_id, r.original_filename, a.job_id, j.title, j.description, a.match_score,
            a.matching_analysis, a.created_at FROM analysis_results a INNER JOIN resumes r
            ON a.resume_id = r.id INNER JOIN job_descriptions j ON a.job_id = j.id WHERE a.id = %s;"""

    with get_connection() as connection:
        result = connection.execute(query, (analysis_id,)).fetchone()

    if not result:
        return None

    return {
        "analysis_id": result[0], "resume_id": result[1], "resume_filename": result[2], "job_id": result[3],
        "job_title": result[4], "job_description": result[5], "match_score": float(result[6]),
        "matching_analysis": result[7], "created_at": result[8], "recommendations": get_recommendations(analysis_id)
    }