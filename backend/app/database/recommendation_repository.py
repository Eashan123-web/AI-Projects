
from psycopg.types.json import Jsonb

from app.database.db import get_connection

def save_recommendations(analysis_id: int, recommendation_data):
    query = """INSERT INTO recommendations (analysis_id, recommendation_data) VALUES (%s, %s) RETURNING id, analysis_id,
      recommendation_data, created_at;"""

    with get_connection() as connection:
        result = connection.execute(query,(analysis_id, Jsonb(recommendation_data))).fetchone()

    return {
        "id": result[0], "analysis_id": result[1], "recommendation_data": result[2], "created_at": result[3]
    }

def get_recommendations(analysis_id: int):
    query = """SELECT id, analysis_id, recommendation_data, created_at FROM recommendations WHERE analysis_id = %s
        ORDER BY id DESC;"""

    with get_connection() as connection:
        results = connection.execute(query, (analysis_id,)).fetchall()

    return [{
            "id": row[0], "analysis_id": row[1], "recommendation_data": row[2], "created_at": row[3]
        }
        for row in results
    ]