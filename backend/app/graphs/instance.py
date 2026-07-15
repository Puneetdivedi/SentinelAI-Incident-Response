"""Process-wide investigation graph + runner.

The compiled graph and its checkpointer are singletons so the human-approval interrupt can
be resumed across separate HTTP requests within a process.

NOTE: the default in-memory checkpointer does not survive a process restart and is not
shared across workers. In production, swap ``MemorySaver`` for a durable LangGraph
checkpointer (e.g. Postgres) — this is the single place to change.
"""

from __future__ import annotations

from functools import lru_cache

from langgraph.checkpoint.memory import MemorySaver

from app.graphs.factory import build_default_investigation_graph
from app.graphs.runner import InvestigationGraphRunner


@lru_cache
def get_investigation_runner() -> InvestigationGraphRunner:
    graph = build_default_investigation_graph(checkpointer=MemorySaver())
    return InvestigationGraphRunner(graph)
