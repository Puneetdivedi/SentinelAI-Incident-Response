"""Supervisor graph assembly.

Wires the registry's nodes into the flow described in the architecture:

    START → supervisor → planner
          → (parallel) alert · log · metrics · deployment · dependency
          → correlation → historical → root_cause → reflection
          → [gaps? loop back to planner] → recommendation → incident_report
          → HUMAN APPROVAL (interrupt) → notification → persist → END

Conditional routing handles the reflection loop-back and the approve/reject branch.
Execution pauses before the human-approval node via ``interrupt_before`` and resumes once a
decision is written to state. A checkpointer makes runs durable and resumable.
"""

from __future__ import annotations

from typing import Any

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph

from app.config.logging import get_logger
from app.domain.enums import AgentName
from app.graphs.registry import NodeRegistry
from app.state.investigation_state import InvestigationState

logger = get_logger(__name__)

HUMAN_APPROVAL = "human_approval"
PERSIST = "persist"

_PARALLEL_ANALYSTS = [
    AgentName.ALERT_ANALYSIS,
    AgentName.LOG_ANALYSIS,
    AgentName.METRICS_ANALYSIS,
    AgentName.DEPLOYMENT_ANALYSIS,
    AgentName.DEPENDENCY_ANALYSIS,
]


async def _human_approval_node(state: InvestigationState) -> dict[str, Any]:
    """Structural node reached only after a human decision has been recorded."""
    return {"current_node": HUMAN_APPROVAL, "completed_nodes": [HUMAN_APPROVAL]}


async def _persist_node(state: InvestigationState) -> dict[str, Any]:
    """Terminal marker. Durable persistence of the final state is performed by the
    investigation service once the graph run (or interrupt cycle) completes (Phase 7)."""
    return {"current_node": PERSIST, "completed_nodes": [PERSIST]}


def build_investigation_graph(
    registry: NodeRegistry,
    *,
    checkpointer: Any | None = None,
    max_reflection_passes: int = 2,
):
    """Compile and return the supervisor graph.

    ``max_reflection_passes`` bounds how many times the reflection node may run; each run
    beyond the first corresponds to one re-plan loop, guaranteeing termination.
    """

    def route_after_reflection(state: InvestigationState) -> str:
        gaps = state.get("reflection_gaps", [])
        passes = state.get("reflection_passes", 0)
        if gaps and passes < max_reflection_passes:
            logger.info("graph.reflection_loopback", extra={"passes": passes})
            return AgentName.PLANNER.value
        return AgentName.RECOMMENDATION.value

    def route_after_approval(state: InvestigationState) -> str:
        if state.get("human_approval_status") == "approved":
            return AgentName.NOTIFICATION.value
        return PERSIST

    graph: StateGraph = StateGraph(InvestigationState)

    # Register agent nodes.
    for name, fn in registry.items():
        graph.add_node(name.value, fn)
    # Register structural nodes.
    graph.add_node(HUMAN_APPROVAL, _human_approval_node)
    graph.add_node(PERSIST, _persist_node)

    # Linear head.
    graph.add_edge(START, AgentName.SUPERVISOR.value)
    graph.add_edge(AgentName.SUPERVISOR.value, AgentName.PLANNER.value)

    # Fan-out to the parallel analysts, fan-in to correlation.
    for analyst in _PARALLEL_ANALYSTS:
        graph.add_edge(AgentName.PLANNER.value, analyst.value)
        graph.add_edge(analyst.value, AgentName.CORRELATION.value)

    # Reasoning chain.
    graph.add_edge(AgentName.CORRELATION.value, AgentName.HISTORICAL_INCIDENT.value)
    graph.add_edge(AgentName.HISTORICAL_INCIDENT.value, AgentName.ROOT_CAUSE.value)
    graph.add_edge(AgentName.ROOT_CAUSE.value, AgentName.REFLECTION.value)

    # Reflection → (loop back to planner) | recommendation.
    graph.add_conditional_edges(
        AgentName.REFLECTION.value,
        route_after_reflection,
        {
            AgentName.PLANNER.value: AgentName.PLANNER.value,
            AgentName.RECOMMENDATION.value: AgentName.RECOMMENDATION.value,
        },
    )

    graph.add_edge(AgentName.RECOMMENDATION.value, AgentName.INCIDENT_REPORT.value)
    graph.add_edge(AgentName.INCIDENT_REPORT.value, HUMAN_APPROVAL)

    # Human approval → (approved → notify) | (rejected → persist).
    graph.add_conditional_edges(
        HUMAN_APPROVAL,
        route_after_approval,
        {AgentName.NOTIFICATION.value: AgentName.NOTIFICATION.value, PERSIST: PERSIST},
    )

    graph.add_edge(AgentName.NOTIFICATION.value, PERSIST)
    graph.add_edge(PERSIST, END)

    return graph.compile(
        checkpointer=checkpointer or MemorySaver(),
        interrupt_before=[HUMAN_APPROVAL],
    )
