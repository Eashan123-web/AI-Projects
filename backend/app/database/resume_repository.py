from app.database.db import get_connection

def save_resume_metadata(filename: str, original_filename: str, file_type: str, file_size: int, storage_path: str):
    query = """INSERT INTO resumes (filename, original_filename, file_type, file_size, storage_path)
        VALUES (%s, %s, %s, %s, %s) RETURNING id, filename, original_filename, file_type, file_size, storage_path,
                  created_at;"""
    
    with get_connection() as connection:
        result = connection.execute(query, (filename, original_filename, file_type, file_size, storage_path)).fetchone()

    return {
        "id": result[0], "filename": result[1], "original_filename": result[2], "file_type": result[3],
        "file_size": result[4], "storage_path": result[5], "created_at": result[6]
    }

def get_resume_by_filename(filename: str):
    query = """SELECT id, filename, original_filename, file_type, file_size, storage_path, created_at FROM resumes
        WHERE filename = %s;"""

    with get_connection() as connection:
        result = connection.execute(query, (filename,)).fetchone()

    if not result:
        return None

    return {
        "id": result[0], "filename": result[1], "original_filename": result[2], "file_type": result[3],
        "file_size": result[4], "storage_path": result[5], "created_at": result[6]
    }