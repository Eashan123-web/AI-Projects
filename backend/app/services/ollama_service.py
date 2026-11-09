
import json
import urllib.error
import urllib.request
import os

OLLAMA_API_URL = os.getenv("OLLAMA_API_URL", "http://localhost:11434/api/generate")

OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:3b")

def generate_ai_response(prompt: str, system_prompt: str = None):
    """Generate an AI response using the local Ollama model."""

    if not prompt or not prompt.strip():
        raise ValueError("Prompt cannot be empty.")

    payload = {
        "model": OLLAMA_MODEL, "prompt": prompt, "stream": False, "options": { "temperature": 0.3 }
    }

    if system_prompt:
        payload["system"] = system_prompt

    request_data = json.dumps(payload).encode("utf-8")

    request = urllib.request.Request(
        OLLAMA_API_URL, data=request_data, headers={ "Content-Type": "application/json" }, method="POST")

    try:
        with urllib.request.urlopen(request, timeout=180) as response:

            result = json.loads(response.read().decode("utf-8"))

            ai_response = result.get("response", "").strip()

            if not ai_response:
                raise RuntimeError("Ollama returned an empty response.")

            return ai_response

    except urllib.error.URLError as error:
        raise RuntimeError(f"Could not connect to Ollama: {error}") from error

    except TimeoutError as error:
        raise RuntimeError("Ollama request timed out.") from error