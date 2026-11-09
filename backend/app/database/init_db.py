
from app.database.db import get_connection

def initialize_database():

    create_table_queries = [
        """CREATE TABLE IF NOT EXISTS resumes (id BIGSERIAL PRIMARY KEY, filename VARCHAR(255) UNIQUE NOT NULL,
            original_filename VARCHAR(255) NOT NULL, file_type VARCHAR(10) NOT NULL, file_size BIGINT NOT NULL,
            storage_path TEXT NOT NULL, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);""",
        """CREATE TABLE IF NOT EXISTS job_descriptions (id BIGSERIAL PRIMARY KEY, title VARCHAR(255),
            description TEXT NOT NULL, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);""",
        """CREATE TABLE IF NOT EXISTS analysis_results (id BIGSERIAL PRIMARY KEY,
            resume_id BIGINT NOT NULL REFERENCES resumes(id) ON DELETE CASCADE,
            job_id BIGINT NOT NULL REFERENCES job_descriptions(id) ON DELETE CASCADE, match_score NUMERIC(5,2) NOT NULL,
            matching_analysis JSONB NOT NULL, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);""",
        """CREATE TABLE IF NOT EXISTS recommendations (id BIGSERIAL PRIMARY KEY,
            analysis_id BIGINT NOT NULL REFERENCES analysis_results(id) ON DELETE CASCADE,
            recommendation_data JSONB NOT NULL, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);""",    
        """CREATE TABLE IF NOT EXISTS resume_chunks (id BIGSERIAL PRIMARY KEY,
            resume_id BIGINT NOT NULL REFERENCES resumes(id) ON DELETE CASCADE, chunk_index INTEGER NOT NULL,
            chunk_text TEXT NOT NULL, embedding JSONB NOT NULL, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE (resume_id, chunk_index));""",
        """CREATE INDEX IF NOT EXISTS idx_resume_chunks_resume_id ON resume_chunks(resume_id);"""
    ]

    with get_connection() as connection:
        for query in create_table_queries:
            connection.execute(query)

    print("Database tables created successfully!")

if __name__ == "__main__":
    initialize_database()