"""Graph tests: orchestration, parallel fan-out, interrupt/resume, reflection loop, retries."""

from __future__ import annotations

import pytest

from app.domain.enums import AgentName
from app.graphs.baseline_nodes import build_baseline_registry
from app.graphs.registry import build_registry
from app.graphs.runner import InvestigationGraphRunner
from app.graphs.supervisor_graph import HUMAN_APPROVAL, build_investigation_graph
from app.state.investigation_state import build_initial_state

INCIDENT = build_initial_state(
    incident_id="INC-TEST-1",
    incident_description="Users cannot log in; auth API returns HTTP 500.",
    affected_service="auth-api",
)


def _runner():
    graph = build_investigation_graph(build_baseline_registry())
    return InvestigationGraphRunner(graph)


async def test_runs_to_human_approval_interrupt() -> None:
    runner = _runner()
    state = await runner.start(dict(INCIDENT), thread_id="t1")

    # Paused before human approval, with all evidence and a report ready.
    assert await runner.is_awaiting_approval(thread_id="t1") is True
    assert state["alerts"] and state["logs"] and state["metrics"]
    assert state["deployments"] and state["dependencies"]
    assert state["timeline"], "correlation should have produced a timeline"
    assert state["root_cause_candidates"]
    assert state["recommendations"]
    assert state["reports"], "an incident report must be generated before approval"
    # Notification must NOT have run yet (it is post-approval).
    assert not state.get("notifications")


async def test_parallel_analysts_all_contribute() -> None:
    runner = _runner()
    state = await runner.start(dict(INCIDENT), thread_id="t-par")
    for analyst in (
        AgentName.ALERT_ANALYSIS,
        AgentName.LOG_ANALYSIS,
        AgentName.METRICS_ANALYSIS,
        AgentName.DEPLOYMENT_ANALYSIS,
        AgentName.DEPENDENCY_ANALYSIS,
    ):
        assert analyst.value in state["completed_nodes"]


async def test_resume_approved_runs_notification_and_completes() -> None:
    runner = _runner()
    await runner.start(dict(INCIDENT), thread_id="t2")
    final = await runner.resume(thread_id="t2", approved=True)

    assert final["human_approval_status"] == "approved"
    assert final["notifications"], "approved runs must notify"
    assert "persist" in final["completed_nodes"]
    assert await runner.is_awaiting_approval(thread_id="t2") is False


async def test_resume_rejected_skips_notification() -> None:
    runner = _runner()
    await runner.start(dict(INCIDENT), thread_id="t3")
    final = await runner.resume(thread_id="t3", approved=False)

    assert final["human_approval_status"] == "rejected"
    assert not final.get("notifications"), "rejected runs must not notify"
    assert "persist" in final["completed_nodes"]


async def test_root_cause_identifies_bad_deployment() -> None:
    runner = _runner()
    state = await runner.start(dict(INCIDENT), thread_id="t4")
    top = max(state["root_cause_candidates"], key=lambda c: c["confidence"])
    assert top["category"] == "bad_deployment"
    assert top["confidence"] >= 0.5


async def test_reflection_loopback_on_low_confidence() -> None:
    """A low-confidence root cause should force one re-plan loop through the planner."""

    async def weak_root_cause(state):
        return {
            "root_cause_candidates": [
                {"category": "unknown", "title": "weak", "reasoning": "n/a",
                 "confidence": 0.2, "evidence": [], "supporting_logs": [],
                 "supporting_metrics": []}
            ],
            "confidence_scores": {"root_cause": 0.2},
        }

    baseline = build_baseline_registry()
    from app.graphs import baseline_nodes

    raw = {
        AgentName.SUPERVISOR: baseline_nodes.supervisor,
        AgentName.PLANNER: baseline_nodes.planner,
        AgentName.ALERT_ANALYSIS: baseline_nodes.alert_analysis,
        AgentName.LOG_ANALYSIS: baseline_nodes.log_analysis,
        AgentName.METRICS_ANALYSIS: baseline_nodes.metrics_analysis,
        AgentName.DEPLOYMENT_ANALYSIS: baseline_nodes.deployment_analysis,
        AgentName.DEPENDENCY_ANALYSIS: baseline_nodes.dependency_analysis,
        AgentName.CORRELATION: baseline_nodes.correlation,
        AgentName.HISTORICAL_INCIDENT: baseline_nodes.historical_incident,
        AgentName.ROOT_CAUSE: weak_root_cause,
        AgentName.REFLECTION: baseline_nodes.reflection,
        AgentName.RECOMMENDATION: baseline_nodes.recommendation,
        AgentName.INCIDENT_REPORT: baseline_nodes.incident_report,
        AgentName.NOTIFICATION: baseline_nodes.notification,
    }
    graph = build_investigation_graph(build_registry(raw), max_reflection_passes=2)
    runner = InvestigationGraphRunner(graph)

    state = await runner.start(dict(INCIDENT), thread_id="t5")
    # Planner ran at least twice (initial + one re-plan) and reflection ran twice.
    assert state["completed_nodes"].count(AgentName.PLANNER.value) >= 2
    assert state["reflection_passes"] >= 2
    # It still reaches the approval interrupt.
    assert await runner.is_awaiting_approval(thread_id="t5") is True


async def test_node_failure_is_recorded_and_graph_continues() -> None:
    """A node that always raises should exhaust retries, record an error, and not halt."""

    async def boom(state):
        raise RuntimeError("simulated dependency-agent failure")

    from app.graphs import baseline_nodes

    raw = {
        AgentName.SUPERVISOR: baseline_nodes.supervisor,
        AgentName.PLANNER: baseline_nodes.planner,
        AgentName.ALERT_ANALYSIS: baseline_nodes.alert_analysis,
        AgentName.LOG_ANALYSIS: baseline_nodes.log_analysis,
        AgentName.METRICS_ANALYSIS: baseline_nodes.metrics_analysis,
        AgentName.DEPLOYMENT_ANALYSIS: baseline_nodes.deployment_analysis,
        AgentName.DEPENDENCY_ANALYSIS: boom,
        AgentName.CORRELATION: baseline_nodes.correlation,
        AgentName.HISTORICAL_INCIDENT: baseline_nodes.historical_incident,
        AgentName.ROOT_CAUSE: baseline_nodes.root_cause,
        AgentName.REFLECTION: baseline_nodes.reflection,
        AgentName.RECOMMENDATION: baseline_nodes.recommendation,
        AgentName.INCIDENT_REPORT: baseline_nodes.incident_report,
        AgentName.NOTIFICATION: baseline_nodes.notification,
    }
    graph = build_investigation_graph(build_registry(raw, max_retries=1))
    runner = InvestigationGraphRunner(graph)

    state = await runner.start(dict(INCIDENT), thread_id="t6")
    assert any(e["agent"] == AgentName.DEPENDENCY_ANALYSIS.value for e in state["errors"])
    # Despite the failure, the pipeline still produced a report and paused for approval.
    assert state["reports"]
    assert await runner.is_awaiting_approval(thread_id="t6") is True
