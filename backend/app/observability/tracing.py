"""LangFuse tracing helpers.

One trace per investigation (keyed by investigation id, which is also the session id) and
one span per agent node capturing latency, confidence, retries, and errors — so the full
execution graph is reconstructable in LangFuse even when the deterministic mock LLM is used.
Token usage / cost are attached by the Anthropic provider's LangChain callback for real runs.

Every call is best-effort and safe when LangFuse is unconfigured (helpers become no-ops).
"""

from __future__ import annotations

from app.config.logging import get_logger
from app.observability.langfuse_client import get_langfuse
from app.prompts.agent_prompts import PROMPT_VERSION

logger = get_logger(__name__)


def start_investigation_trace(
    *, investigation_id: str, incident_description: str
) -> str | None:
    """Create the top-level trace for an investigation. Returns the trace id, or None."""
    client = get_langfuse()
    if client is None:
        return None
    try:
        client.trace(
            id=investigation_id,
            name="investigation",
            session_id=investigation_id,
            input={"incident": incident_description},
            metadata={"prompt_version": PROMPT_VERSION},
        )
        return investigation_id
    except Exception as exc:  # noqa: BLE001
        logger.warning("langfuse.trace_failed", extra={"error": str(exc)})
        return None


def record_agent_span(
    *,
    trace_id: str | None,
    agent: str,
    latency_ms: float,
    attempt: int,
    confidence: float | None = None,
    error: str | None = None,
) -> None:
    """Record a per-agent span under the investigation trace (best-effort)."""
    client = get_langfuse()
    if client is None or not trace_id:
        return
    try:
        client.span(
            trace_id=trace_id,
            name=agent,
            level="ERROR" if error else "DEFAULT",
            status_message=error,
            metadata={
                "agent": agent,
                "prompt_version": PROMPT_VERSION,
                "latency_ms": round(latency_ms, 2),
                "attempts": attempt,
                "confidence": confidence,
            },
        )
    except Exception as exc:  # noqa: BLE001
        logger.warning("langfuse.span_failed", extra={"agent": agent, "error": str(exc)})
