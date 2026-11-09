
import math

from psycopg.types.json import Jsonb
from app.database.db import get_connection

def save_resume_chunks(
    resume_id: int,
    chunks: list[dict],
    embeddings: list[list[float]]
):
    """Save resume chunks and their embedding vectors."""

    if len(chunks) != len(embeddings):
        raise ValueError("Chunks and embeddings must have the same length.")

    if not chunks:
        return 0

    for embedding in embeddings:
        if not embedding or not all(
            isinstance(value, (int, float))
            and not isinstance(value, bool)
            and math.isfinite(value)
            for value in embedding
        ):
            raise ValueError("Invalid embedding vector.")

    with get_connection() as connection:

        connection.execute("DELETE FROM resume_chunks WHERE resume_id = %s", (resume_id,))

        for chunk, embedding in zip(chunks, embeddings):

            connection.execute(
                """INSERT INTO resume_chunks (resume_id, chunk_index, chunk_text, embedding) VALUES (%s, %s, %s, %s)""",
                (resume_id, chunk["chunk_index"], chunk["text"], Jsonb(embedding)))

    return len(chunks)

def get_resume_chunks(resume_id: int):
    """Retrieve all stored chunks for a resume."""

    query = """SELECT id, resume_id, chunk_index, chunk_text, embedding, created_at FROM resume_chunks
        WHERE resume_id = %s ORDER BY chunk_index;"""

    with get_connection() as connection:
        results = connection.execute(query, (resume_id,)).fetchall()

    return [
        {
            "id": row[0], "resume_id": row[1], "chunk_index": row[2], "text": row[3], "embedding": row[4],
            "created_at": row[5]
        }
        for row in results
    ]

def calculate_cosine_similarity(vector_a: list[float], vector_b: list[float]) -> float:
    """Calculate cosine similarity between two vectors."""

    if len(vector_a) != len(vector_b):
        raise ValueError("Embedding dimensions must match.")

    if not vector_a:
        raise ValueError("Embedding vectors cannot be empty.")

    dot_product = sum(a * b for a, b in zip(vector_a, vector_b))

    magnitude_a = math.sqrt(sum(a * a for a in vector_a))
    magnitude_b = math.sqrt(sum(b * b for b in vector_b))

    if magnitude_a == 0 or magnitude_b == 0:
        return 0.0

    return dot_product / (magnitude_a * magnitude_b)

def search_similar_chunks(resume_id: int, query_embedding: list[float], top_k: int = 5):
    """Retrieve the most relevant resume chunks."""

    if not query_embedding or not all(
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(value)
        for value in query_embedding
    ):
        raise ValueError("Invalid query embedding.")

    if top_k <= 0:
        raise ValueError("top_k must be greater than zero.")

    stored_chunks = get_resume_chunks(resume_id)

    results = []

    for chunk in stored_chunks:

        similarity = calculate_cosine_similarity(query_embedding, chunk["embedding"])

        results.append({
            "chunk_index": chunk["chunk_index"],
            "text": chunk["text"],
            "similarity": similarity
        })

    results.sort(key=lambda item: item["similarity"], reverse=True)

    return results[:top_k]