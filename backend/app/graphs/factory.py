"""Convenience factory for the default LLM-backed investigation graph."""

from __future__ import annotations

from typing import Any

from app.agents.registry import build_agent_registry
from app.graphs.supervisor_graph import build_investigation_graph
from app.infrastructure.llm.base import LLMProvider
from app.infrastructure.llm.factory import get_llm_provider


def build_default_investigation_graph(
    *,
    llm: LLMProvider | None = None,
    checkpointer: Any | None = None,
    max_reflection_passes: int = 2,
):
    """Build the supervisor graph wired to real agents (LLM provider from settings)."""
    provider = llm or get_llm_provider()
    registry = build_agent_registry(provider)
    return build_investigation_graph(
        registry, checkpointer=checkpointer, max_reflection_passes=max_reflection_passes
    )
