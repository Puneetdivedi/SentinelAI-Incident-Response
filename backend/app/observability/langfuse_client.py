"""LangFuse client access.

Returns a cached LangFuse client when configured (keys present AND the package installed),
otherwise ``None`` so all instrumentation degrades to a no-op. This keeps the platform fully
functional offline and in tests without any LangFuse dependency.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Any

from app.config.logging import get_logger
from app.config.settings import get_settings

logger = get_logger(__name__)


@lru_cache
def get_langfuse() -> Any | None:
    settings = get_settings()
    if not settings.langfuse_enabled:
        return None
    try:
        from langfuse import Langfuse
    except ImportError:
        logger.warning("langfuse.not_installed")
        return None
    try:
        return Langfuse(
            public_key=settings.langfuse_public_key,
            secret_key=settings.langfuse_secret_key,
            host=settings.langfuse_host,
        )
    except Exception as exc:  # noqa: BLE001 - never let observability break startup
        logger.warning("langfuse.init_failed", extra={"error": str(exc)})
        return None


def langfuse_trace_url(trace_id: str | None) -> str | None:
    """Build a shareable trace URL for an investigation."""
    if not trace_id:
        return None
    settings = get_settings()
    return f"{settings.langfuse_host.rstrip('/')}/trace/{trace_id}"


def get_langchain_callback() -> Any | None:
    """Return a LangFuse LangChain callback handler for token/cost capture, or None."""
    if get_langfuse() is None:
        return None
    settings = get_settings()
    try:
        from langfuse.callback import CallbackHandler

        return CallbackHandler(
            public_key=settings.langfuse_public_key,
            secret_key=settings.langfuse_secret_key,
            host=settings.langfuse_host,
        )
    except Exception as exc:  # noqa: BLE001
        logger.warning("langfuse.callback_failed", extra={"error": str(exc)})
        return None


def flush() -> None:
    """Flush buffered events (best-effort)."""
    client = get_langfuse()
    if client is not None:
        try:
            client.flush()
        except Exception as exc:  # noqa: BLE001
            logger.warning("langfuse.flush_failed", extra={"error": str(exc)})
