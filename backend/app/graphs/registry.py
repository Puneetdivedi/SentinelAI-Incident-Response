"""Node registry and shared node instrumentation.

The graph is assembled against a registry mapping each ``AgentName`` to an async node
function. Phase 4 provides a deterministic baseline registry; Phase 5 supplies an
LLM-backed agent registry with the same shape, so the graph wiring never changes.

Every node is wrapped with ``instrument`` which adds bounded retries, latency capture,
error recording into state, and ``completed_nodes`` / ``current_node`` bookkeeping.
"""

from __future__ import annotations

import time
from collections.abc import Awaitable, Callable
from typing import Any

from app.config.logging import get_logger
from app.domain.enums import AgentName
from app.state.investigation_state import InvestigationState

logger = get_logger(__name__)

# A node consumes the current state and returns a partial state update.
NodeFn = Callable[[InvestigationState], Awaitable[dict[str, Any]]]

NodeRegistry = dict[AgentName, NodeFn]

DEFAULT_MAX_RETRIES = 2


def instrument(name: AgentName, fn: NodeFn, *, max_retries: int = DEFAULT_MAX_RETRIES) -> NodeFn:
    """Wrap a node with retries, timing, and error/bookkeeping state updates."""

    async def _wrapped(state: InvestigationState) -> dict[str, Any]:
        attempt = 0
        last_error: Exception | None = None
        started = time.perf_counter()

        while attempt <= max_retries:
            try:
                update = await fn(state)
                latency_ms = (time.perf_counter() - started) * 1000
                logger.info(
                    "node.completed",
                    extra={
                        "agent": name.value,
                        "attempt": attempt,
                        "latency_ms": round(latency_ms, 2),
                    },
                )
                # Merge bookkeeping without clobbering the node's own updates.
                update.setdefault("current_node", name.value)
                update["completed_nodes"] = [name.value]
                return update
            except Exception as exc:  # noqa: BLE001 - recorded into state, not swallowed
                last_error = exc
                attempt += 1
                logger.warning(
                    "node.retry",
                    extra={"agent": name.value, "attempt": attempt, "error": str(exc)},
                )

        logger.error("node.failed", extra={"agent": name.value, "error": str(last_error)})
        return {
            "current_node": name.value,
            "completed_nodes": [name.value],
            "errors": [
                {
                    "agent": name.value,
                    "error": str(last_error),
                    "attempts": attempt,
                }
            ],
            "retry_counts": {name.value: attempt},
        }

    return _wrapped


def build_registry(raw: dict[AgentName, NodeFn], *, max_retries: int = DEFAULT_MAX_RETRIES) -> NodeRegistry:
    """Instrument every node function in a raw mapping."""
    return {name: instrument(name, fn, max_retries=max_retries) for name, fn in raw.items()}
