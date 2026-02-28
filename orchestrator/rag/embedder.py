"""
Embedding utility using Gemini REST API directly (v1 endpoint).
Tries text-embedding-004 (768-dim) first; falls back to embedding-001 (768-dim).
Uses httpx (already in requirements) to call the v1 REST API directly,
since the google-genai SDK uses v1beta which doesn't support embedding models.
"""
import os
import logging
import httpx

logger = logging.getLogger(__name__)

_EMBED_DIM = 768
_API_BASE = "https://generativelanguage.googleapis.com/v1/models"

# Models to try in order — both produce 768-dim vectors
_EMBED_MODELS = ["text-embedding-004", "embedding-001"]
_active_model = None  # cached after first successful call


def _get_api_key() -> str:
    key = os.getenv("GEMINI_API_KEY")
    if not key:
        raise RuntimeError("GEMINI_API_KEY not set — cannot create embeddings")
    return key


def _try_embed(model: str, texts: list[str], api_key: str) -> list[list[float]] | None:
    """Attempt batch embedding with a specific model. Returns None on failure."""
    url = f"{_API_BASE}/{model}:batchEmbedContents?key={api_key}"
    requests_payload = [
        {"model": f"models/{model}", "content": {"parts": [{"text": t}]}}
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
        logger.warning("[EMBEDDER] Model %s failed: %s", model, str(e)[:200])
        return None


def embed_texts(texts: list[str]) -> list[list[float]]:
    global _active_model
    api_key = _get_api_key()

    # Use cached model if we already found one that works
    if _active_model:
        result = _try_embed(_active_model, texts, api_key)
        if result is not None:
            return result
        # Cached model failed — reset and retry all
        logger.warning("[EMBEDDER] Cached model %s failed, retrying all models", _active_model)
        _active_model = None

    # Try each model in order
    for model in _EMBED_MODELS:
        result = _try_embed(model, texts, api_key)
        if result is not None:
            _active_model = model
            logger.info("[EMBEDDER] Using model: %s", model)
            return result

    # All models failed — return zero vectors so app still starts
    logger.error("[EMBEDDER] All embedding models failed. Returning zero vectors.")
    return [[0.0] * _EMBED_DIM for _ in texts]


def embed_query(query: str) -> list[float]:
    return embed_texts([query])[0]
