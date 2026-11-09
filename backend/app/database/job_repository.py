
from app.database.db import get_connection

def save_job_description(description: str, title: str = None):
    query = """INSERT INTO job_descriptions (title, description) VALUES (%s, %s)
        RETURNING id, title, description, created_at;"""

    with get_connection() as connection:
        result = connection.execute(query, (title, description)).fetchone()

    return {
        "id": result[0], "title": result[1], "description": result[2], "created_at": result[3]
    }

def get_job_description(job_id: int):
    query = """SELECT id, title, description, created_at FROM job_descriptions WHERE id = %s;"""

    with get_connection() as connection:
        result = connection.execute(query, (job_id,)).fetchone()

    if not result:
        return None

    return {
        "id": result[0], "title": result[1], "description": result[2], "created_at": result[3]
    }