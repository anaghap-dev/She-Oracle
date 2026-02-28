"""
Embedding utility using Gemini REST API directly (v1 endpoint).
Model: text-embedding-004 — free tier, 768-dim, no local model download.
Uses httpx (already in requirements) to call the v1 REST API directly,
since the google-genai SDK uses v1beta which doesn't support embedding models.
"""
import os
import logging
import httpx

logger = logging.getLogger(__name__)

EMBED_MODEL = "text-embedding-004"
_EMBED_DIM = 768
_API_BASE = "https://generativelanguage.googleapis.com/v1/models"


def _get_api_key() -> str:
    key = os.getenv("GEMINI_API_KEY")
    if not key:
        raise RuntimeError("GEMINI_API_KEY not set — cannot create embeddings")
    return key


def embed_texts(texts: list[str]) -> list[list[float]]:
    api_key = _get_api_key()
    url = f"{_API_BASE}/{EMBED_MODEL}:batchEmbedContents?key={api_key}"

    # Build batch request
    requests_payload = [
        {"model": f"models/{EMBED_MODEL}", "content": {"parts": [{"text": t}]}}
        for t in texts
    ]

    try:
        response = httpx.post(
            url,
            json={"requests": requests_payload},
            timeout=30.0,
        )
        response.raise_for_status()
        data = response.json()
        return [item["values"] for item in data["embeddings"]]
    except Exception as e:
        logger.error("[EMBEDDER] Batch embed failed: %s", str(e)[:200])
        # Return zero vectors as fallback
        return [[0.0] * _EMBED_DIM for _ in texts]


def embed_query(query: str) -> list[float]:
    return embed_texts([query])[0]
