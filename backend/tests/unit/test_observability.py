"""Observability degrades gracefully when LangFuse is not configured."""

from __future__ import annotations

from app.observability.langfuse_client import get_langfuse, langfuse_trace_url
from app.observability.tracing import record_agent_span, start_investigation_trace


def test_langfuse_disabled_by_default() -> None:
    # Test settings carry no LangFuse keys.
    assert get_langfuse() is None


def test_trace_url_helper() -> None:
    assert langfuse_trace_url(None) is None
    url = langfuse_trace_url("abc-123")
    assert url is not None and url.endswith("/trace/abc-123")


def test_start_trace_noop_when_disabled() -> None:
    assert start_investigation_trace(
        investigation_id="i1", incident_description="x"
    ) is None


def test_record_span_noop_when_disabled() -> None:
    # Must not raise even with a trace_id and an error.
    record_agent_span(
        trace_id="i1", agent="root_cause", latency_ms=12.3, attempt=0, confidence=0.9
    )
    record_agent_span(
        trace_id="i1", agent="log_analysis", latency_ms=5.0, attempt=2, error="boom"
    )
