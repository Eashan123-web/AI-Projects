
import json
import urllib.error
import urllib.request
import os

OLLAMA_EMBEDDING_URL = os.getenv("OLLAMA_EMBEDDING_URL", "http://localhost:11434/api/embed")

def generate_embeddings(texts: list[str]) -> list[list[float]]:
    """Generate embedding vectors for multiple text chunks using Ollama."""

    if not texts:
        return []

    if not all(isinstance(text, str) and text.strip() for text in texts):
        raise ValueError("All input texts must be non-empty strings.")

    payload = {
        "model": EMBEDDING_MODEL, "input": texts
    }

    request_data = json.dumps(payload).encode("utf-8")

    request = urllib.request.Request(
        OLLAMA_EMBEDDING_URL, data=request_data, headers={"Content-Type": "application/json"}, method="POST"
    )

    try:
        with urllib.request.urlopen(request, timeout=180) as response:
            result = json.loads(response.read().decode("utf-8"))

        embeddings = result.get("embeddings")

        if not isinstance(embeddings, list):
            raise RuntimeError("Ollama returned an invalid embedding response.")

        if len(embeddings) != len(texts):
            raise RuntimeError("Embedding count does not match input text count.")

        for embedding in embeddings:
            if (
                not isinstance(embedding, list)
                or not embedding
                or not all(
                    isinstance(value, (int, float)) and not isinstance(value, bool)
                    for value in embedding
                )
            ):
                raise RuntimeError("Ollama returned an invalid embedding vector.")

        return embeddings

    except urllib.error.HTTPError as error:
        error_details = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Ollama embedding API error: {error.code} - {error_details}") from error

    except urllib.error.URLError as error:
        raise RuntimeError(f"Could not connect to Ollama: {error}") from error

    except TimeoutError as error:
        raise RuntimeError("Ollama embedding request timed out.") from error


def generate_embedding(text: str) -> list[float]:
    """Generate an embedding vector for a single text."""

    if not isinstance(text, str) or not text.strip():
        raise ValueError("Input text cannot be empty.")

    embeddings = generate_embeddings([text])

    return embeddings[0]