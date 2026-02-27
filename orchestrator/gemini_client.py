"""
Shared Gemini client using the google-genai SDK.
All agents and tools import generate() from here.

Model cascade: automatically falls back to cheaper/higher-quota models
when the primary model hits quota limits (429) or is unavailable (503).

If ALL models fail, generate() returns GEMINI_UNAVAILABLE_SENTINEL instead
of raising — callers check with is_gemini_response_ok() and fall back
gracefully. The full error is logged at ERROR level for backend visibility.
"""
import os
import time
import logging
from google import genai

logger = logging.getLogger(__name__)

_client = None

# Sentinel string returned when every Gemini model has failed.
# Callers check for this with is_gemini_response_ok().
GEMINI_UNAVAILABLE_SENTINEL = "__GEMINI_UNAVAILABLE__"

# Primary: gemini-2.0-flash (1,500 req/day free tier — much higher than 2.5-flash's 20/day)
# Fallback: gemini-1.5-flash (legacy, very high free quota)
MODEL_CASCADE = [
    "models/gemini-2.5-flash",
]

# Indicators of quota/rate issues — worth retrying with backoff
_QUOTA_ERRORS = ("429", "503", "RESOURCE_EXHAUSTED", "quota", "rate limit")

# Indicators that mean the model itself is unavailable — skip to next model
_MODEL_NOT_FOUND = ("404", "NOT_FOUND", "is not found")

# Retry config for RPM (requests per minute) throttling
# Free tier: 15 RPM. Wait up to ~60s total before giving up on a model.
_MAX_RETRIES_PER_MODEL = 3
_RETRY_DELAYS = [4, 15, 30]   # seconds between retries (exponential-ish)

# Track last known failure reason for the health check
_last_failure_reason: str = ""
_gemini_healthy: bool = True


def _get_client():
    global _client
    if _client is None:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY not set in .env")
        _client = genai.Client(api_key=api_key)
    return _client


def _is_quota_error(exc: Exception) -> bool:
    msg = str(exc)
    return any(ind.lower() in msg.lower() for ind in _QUOTA_ERRORS)


def _is_model_not_found(exc: Exception) -> bool:
    msg = str(exc)
    return any(ind.lower() in msg.lower() for ind in _MODEL_NOT_FOUND)


def is_gemini_response_ok(text: str) -> bool:
    """Return False if text is the unavailability sentinel."""
    return text != GEMINI_UNAVAILABLE_SENTINEL


def gemini_status() -> dict:
    """Return current Gemini health state — used by /health endpoint."""
    return {
        "healthy": _gemini_healthy,
        "last_failure": _last_failure_reason or None,
    }


def generate(prompt: str) -> str:
    """
    Send a prompt to Gemini and return the text response.

    - Retries the same model up to 3 times with backoff on RPM (429) errors.
    - Falls back through MODEL_CASCADE if a model hits daily quota or 404.
    - If ALL models fail, logs the full error and returns GEMINI_UNAVAILABLE_SENTINEL.
    - Never raises — the caller decides what to do on failure.
    """
    global _gemini_healthy, _last_failure_reason

    try:
        client = _get_client()
    except RuntimeError as e:
        _gemini_healthy = False
        _last_failure_reason = str(e)
        logger.error("[GEMINI] Client init failed: %s", e)
        return GEMINI_UNAVAILABLE_SENTINEL

    last_exc = None

    for model in MODEL_CASCADE:
        for attempt in range(_MAX_RETRIES_PER_MODEL):
            try:
                response = client.models.generate_content(
                    model=model,
                    contents=prompt,
                )
                # Successful call — mark healthy
                _gemini_healthy = True
                _last_failure_reason = ""

                if model != MODEL_CASCADE[0]:
                    logger.warning(
                        "[GEMINI] Used fallback model %s (primary unavailable)", model
                    )
                return response.text.strip()

            except Exception as exc:
                last_exc = exc

                if _is_model_not_found(exc):
                    # Model doesn't exist — skip immediately, no retry
                    logger.warning("[GEMINI] Model not found: %s, skipping.", model)
                    break

                if _is_quota_error(exc):
                    # Check if this looks like daily quota (not RPM)
                    # Daily quota error usually says "quota exceeded" without retry hint
                    err_str = str(exc).lower()
                    is_daily = "free_tier_requests" in err_str or "daily" in err_str

                    if is_daily:
                        # Daily quota hit — no point retrying this model
                        logger.warning(
                            "[GEMINI] Daily quota exhausted on %s, trying next model.", model
                        )
                        break

                    # RPM / rate limit — retry with backoff
                    delay = _RETRY_DELAYS[attempt] if attempt < len(_RETRY_DELAYS) else 30
                    logger.warning(
                        "[GEMINI] Rate limited on %s (attempt %d/%d), retrying in %ds. Error: %s",
                        model, attempt + 1, _MAX_RETRIES_PER_MODEL, delay, str(exc)[:120]
                    )
                    time.sleep(delay)
                    continue

                # Non-quota error — log and try next model
                logger.error("[GEMINI] Unexpected error on %s: %s", model, str(exc)[:200])
                break

    # All models exhausted
    reason = (
        f"All Gemini models unavailable. "
        f"Last error: {last_exc}. "
        "Serving fallback responses."
    )
    _gemini_healthy = False
    _last_failure_reason = str(last_exc)
    logger.error("[GEMINI] %s", reason)

    return GEMINI_UNAVAILABLE_SENTINEL
