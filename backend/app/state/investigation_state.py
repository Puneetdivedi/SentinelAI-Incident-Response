"""Strongly-typed LangGraph state for an investigation.

Parallel analysis branches write concurrently, so every key that more than one node may
write in the same super-step uses a reducer (``operator.add`` for append-only lists, a
dict-merge for maps). Single-writer keys use plain assignment (last write wins).
"""

from __future__ import annotations

import operator
from typing import Annotated, Any, TypedDict


def merge_dicts(left: dict[str, Any], right: dict[str, Any]) -> dict[str, Any]:
    """Reducer that shallow-merges two dicts (right wins on key collisions)."""
    merged = dict(left)
    merged.update(right)
    return merged


def take_last(_left: Any, right: Any) -> Any:
    """Reducer that keeps the most recent write.

    Needed for scalar keys that multiple parallel nodes may write in the same super-step
    (e.g. ``current_node``); a plain channel would raise on concurrent updates.
    """
    return right


class InvestigationState(TypedDict, total=False):
    """The full state threaded through the supervisor graph.

    ``total=False`` lets each node return only the keys it changed; LangGraph applies those
    partial updates through the reducers declared below.
    """

    # ── Identity / request ───────────────────────────────────
    incident_id: str
    incident_description: str
    affected_service: str | None

    # ── Planning / control ───────────────────────────────────
    execution_plan: list[str]
    current_node: Annotated[str, take_last]
    completed_nodes: Annotated[list[str], operator.add]

    # ── Collected evidence (append-only; written by parallel branches) ─
    logs: Annotated[list[dict], operator.add]
    alerts: Annotated[list[dict], operator.add]
    metrics: Annotated[list[dict], operator.add]
    deployments: Annotated[list[dict], operator.add]
    dependencies: Annotated[list[dict], operator.add]
    historical_matches: Annotated[list[dict], operator.add]

    # ── Reasoning outputs (single-writer) ────────────────────
    timeline: list[dict]
    root_cause_candidates: list[dict]
    recommendations: list[dict]
    reports: list[dict]
    notifications: list[dict]

    # ── Reflection loop ──────────────────────────────────────
    reflection_gaps: list[str]
    reflection_passes: int

    # ── Confidence / errors / retries (reducer-merged) ───────
    confidence_scores: Annotated[dict[str, float], merge_dicts]
    retry_counts: Annotated[dict[str, int], merge_dicts]
    errors: Annotated[list[dict], operator.add]

    # ── Human-in-the-loop ────────────────────────────────────
    human_approval_status: str  # pending | approved | rejected

    # ── Observability ────────────────────────────────────────
    langfuse_trace_id: str | None
    langfuse_session_id: str | None
    langfuse_run_ids: Annotated[list[str], operator.add]


def build_initial_state(
    *,
    incident_id: str,
    incident_description: str,
    affected_service: str | None = None,
    langfuse_session_id: str | None = None,
) -> InvestigationState:
    """Construct a fully-initialized state for a new investigation."""
    return InvestigationState(
        incident_id=incident_id,
        incident_description=incident_description,
        affected_service=affected_service,
        execution_plan=[],
        current_node="",
        completed_nodes=[],
        logs=[],
        alerts=[],
        metrics=[],
        deployments=[],
        dependencies=[],
        historical_matches=[],
        timeline=[],
        root_cause_candidates=[],
        recommendations=[],
        reports=[],
        notifications=[],
        reflection_gaps=[],
        reflection_passes=0,
        confidence_scores={},
        retry_counts={},
        errors=[],
        human_approval_status="pending",
        langfuse_trace_id=None,
        langfuse_session_id=langfuse_session_id,
        langfuse_run_ids=[],
    )
