
import re


def chunk_text(
    text: str,
    chunk_size: int = 500,
    overlap: int = 80
):
    """
    Split text into smaller chunks with overlapping words.

    Args:
        text: Input resume or job description.
        chunk_size: Maximum words in each chunk.
        overlap: Number of words repeated between chunks.

    Returns:
        List of dictionaries containing chunk details.
    """

    if not text or not text.strip():
        return []

    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than zero.")

    if overlap < 0 or overlap >= chunk_size:
        raise ValueError(
            "overlap must be non-negative and smaller than chunk_size."
        )

    words = re.findall(r"\S+", text)

    chunks = []
    start = 0
    chunk_index = 0
    step = chunk_size - overlap

    while start < len(words):
        end = min(start + chunk_size, len(words))

        chunk_words = words[start:end]
        chunk_content = " ".join(chunk_words)

        chunks.append({
            "chunk_index": chunk_index,
            "text": chunk_content,
            "word_count": len(chunk_words)
        })

        if end == len(words):
            break

        start += step
        chunk_index += 1

    return chunks
