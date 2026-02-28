"""
Embedding utility using Gemini REST API (v1beta endpoint).
Model: gemini-embedding-001 — available on v1beta for all AI Studio keys.
Produces 3072-dim vectors.
Uses httpx (already in requirements).
"""
import os
import logging
import httpx

logger = logging.getLogger(__name__)

EMBED_MODEL = "gemini-embedding-001"
_EMBED_DIM = 3072
_API_BASE = "https://generativelanguage.googleapis.com/v1beta/models"


def _get_api_key() -> str:
    key = os.getenv("GEMINI_API_KEY")
    if not key:
        raise RuntimeError("GEMINI_API_KEY not set — cannot create embeddings")
    return key


def embed_texts(texts: list[str]) -> list[list[float]]:
    api_key = _get_api_key()
    url = f"{_API_BASE}/{EMBED_MODEL}:batchEmbedContents?key={api_key}"

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
        logger.error("[EMBEDDER] Batch embed failed: %s", str(e)[:300])
        return [[0.0] * _EMBED_DIM for _ in texts]


def embed_query(query: str) -> list[float]:
    return embed_texts([query])[0]
