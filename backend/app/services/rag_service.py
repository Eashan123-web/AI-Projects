
from app.services.text_chunking_service import chunk_text
from app.services.embedding_service import (
    generate_embedding,
    generate_embeddings
)

from app.database.vector_repository import (
    save_resume_chunks,
    get_resume_chunks,
    search_similar_chunks
)

def build_resume_rag_context(
    resume_id: int,
    resume_text: str,
    job_description: str,
    top_k: int = 5
):
    """Build and retrieve relevant resume context for a job description."""

    if not resume_text or not resume_text.strip():
        raise ValueError("Resume text cannot be empty.")

    if not job_description or not job_description.strip():
        raise ValueError("Job description cannot be empty.")

    if top_k <= 0:
        raise ValueError("top_k must be greater than zero.")

    # Step 1: Check whether resume chunks already exist.
    stored_chunks = get_resume_chunks(resume_id)

    # Step 2: Create and save chunks if they do not exist.
    if not stored_chunks:

        chunks = chunk_text(
            resume_text, chunk_size=500, overlap=80
        )

        if not chunks:
            return []

        embeddings = generate_embeddings(
            [chunk["text"] for chunk in chunks]
        )

        save_resume_chunks(
            resume_id, chunks, embeddings
        )

    # Step 3: Generate embedding for the job description.
    query_embedding = generate_embedding(job_description)

    # Step 4: Retrieve the most relevant resume chunks.
    relevant_chunks = search_similar_chunks(
        resume_id=resume_id, query_embedding=query_embedding, top_k=top_k
    )

    return relevant_chunks