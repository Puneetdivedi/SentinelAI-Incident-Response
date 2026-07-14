"""High-level driver for the supervisor graph.

Encapsulates the interrupt/resume protocol so callers (the investigation service in Phase 7)
don't manipulate LangGraph config or checkpointer details directly.
"""

from __future__ import annotations

from typing import Any

from app.config.logging import get_logger
from app.graphs.supervisor_graph import HUMAN_APPROVAL
from app.state.investigation_state import InvestigationState

logger = get_logger(__name__)


class InvestigationGraphRunner:
    """Runs an investigation to the human-approval interrupt and resumes it."""

    def __init__(self, graph: Any) -> None:
        self._graph = graph

    @staticmethod
    def _config(thread_id: str) -> dict[str, Any]:
        return {"configurable": {"thread_id": thread_id}}

    async def start(
        self, initial_state: InvestigationState, *, thread_id: str
    ) -> InvestigationState:
        """Run from START until the graph interrupts before human approval (or ends)."""
        config = self._config(thread_id)
        await self._graph.ainvoke(initial_state, config)
        snapshot = await self._graph.aget_state(config)
        logger.info(
            "graph.paused",
            extra={"thread_id": thread_id, "next": list(snapshot.next)},
        )
        return snapshot.values

    async def resume(self, *, thread_id: str, approved: bool) -> InvestigationState:
        """Record the human decision and drive the graph to completion."""
        config = self._config(thread_id)
        await self._graph.aupdate_state(
            config,
            {"human_approval_status": "approved" if approved else "rejected"},
        )
        await self._graph.ainvoke(None, config)
        snapshot = await self._graph.aget_state(config)
        return snapshot.values

    async def is_awaiting_approval(self, *, thread_id: str) -> bool:
        snapshot = await self._graph.aget_state(self._config(thread_id))
        return HUMAN_APPROVAL in tuple(snapshot.next)

    async def get_state(self, *, thread_id: str) -> InvestigationState:
        snapshot = await self._graph.aget_state(self._config(thread_id))
        return snapshot.values
