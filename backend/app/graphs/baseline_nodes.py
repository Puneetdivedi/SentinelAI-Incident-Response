"""Deterministic baseline node implementations.

These are fully-functional (not placeholders): each node reads the state and returns a
valid, coherent partial update, so the whole supervisor graph executes end-to-end without
an LLM or external data. Phase 5 replaces these with LLM-backed agents behind the same
``NodeFn`` contract; Phase 6 swaps the synthetic evidence for the mock data-source tools.

The synthetic evidence is intentionally shaped around the reference incident (a deployment
shortly before an auth-500 spike with DB-connection exhaustion) so the reasoning nodes have
something meaningful to correlate.
"""

from __future__ import annotations

from typing import Any

from app.domain.enums import (
    AgentName,
    RecommendationPriority,
    RemediationAction,
    RiskLevel,
    RootCauseCategory,
)
from app.graphs.registry import NodeRegistry, build_registry
from app.state.investigation_state import InvestigationState

# A fixed reference instant so baseline output is deterministic (no wall-clock reads).
_T0 = "2026-07-14T09:00:00+00:00"
_T_DEPLOY = "2026-07-14T08:55:00+00:00"


async def supervisor(state: InvestigationState) -> dict[str, Any]:
    """Entry node — acknowledges the request and hands off to planning."""
    return {"confidence_scores": {AgentName.SUPERVISOR.value: 1.0}}


async def planner(state: InvestigationState) -> dict[str, Any]:
    """Produce an ordered execution plan for the investigation."""
    plan = [
        "Inspect monitoring alerts",
        "Retrieve and analyze logs",
        "Analyze CPU/memory/latency metrics",
        "Inspect recent deployments",
        "Check dependency health",
        "Correlate evidence into a timeline",
        "Search historical incidents",
        "Determine probable root cause",
        "Recommend remediation",
    ]
    return {"execution_plan": plan, "confidence_scores": {AgentName.PLANNER.value: 1.0}}


async def alert_analysis(state: InvestigationState) -> dict[str, Any]:
    return {
        "alerts": [
            {
                "timestamp": _T0,
                "name": "HighErrorRate",
                "severity": "critical",
                "description": "Auth API 5xx rate above 20% for 5 minutes.",
                "service": state.get("affected_service") or "auth-api",
            }
        ],
        "confidence_scores": {AgentName.ALERT_ANALYSIS.value: 0.9},
    }


async def log_analysis(state: InvestigationState) -> dict[str, Any]:
    return {
        "logs": [
            {
                "timestamp": _T0,
                "source": "fastapi",
                "level": "ERROR",
                "message": "HTTP 500 on POST /login: QueuePool limit reached, "
                "connection timed out.",
                "service": "auth-api",
            },
            {
                "timestamp": _T0,
                "source": "postgresql",
                "level": "WARNING",
                "message": "remaining connection slots are reserved; too many clients.",
                "service": "postgres",
            },
        ],
        "confidence_scores": {AgentName.LOG_ANALYSIS.value: 0.88},
    }


async def metrics_analysis(state: InvestigationState) -> dict[str, Any]:
    return {
        "metrics": [
            {"timestamp": _T0, "metric": "cpu", "value": 92.0, "unit": "%", "service": "auth-api"},
            {"timestamp": _T0, "metric": "memory", "value": 87.0, "unit": "%", "service": "auth-api"},
            {"timestamp": _T0, "metric": "db_connections", "value": 100.0, "unit": "count", "service": "postgres"},
            {"timestamp": _T0, "metric": "latency", "value": 4200.0, "unit": "ms", "service": "auth-api"},
        ],
        "confidence_scores": {AgentName.METRICS_ANALYSIS.value: 0.9},
    }


async def deployment_analysis(state: InvestigationState) -> dict[str, Any]:
    return {
        "deployments": [
            {
                "timestamp": _T_DEPLOY,
                "service": "auth-api",
                "version": "v2.4.0",
                "author": "release-bot",
                "change_summary": "Reduced DB pool size; added synchronous audit write on login.",
                "rollback_available": True,
            }
        ],
        "confidence_scores": {AgentName.DEPLOYMENT_ANALYSIS.value: 0.95},
    }


async def dependency_analysis(state: InvestigationState) -> dict[str, Any]:
    return {
        "dependencies": [
            {"name": "postgres", "healthy": False, "latency_ms": 3800.0, "error_rate": 0.0,
             "detail": "Connection pool exhausted."},
            {"name": "redis", "healthy": True, "latency_ms": 3.0, "error_rate": 0.0, "detail": None},
        ],
        "confidence_scores": {AgentName.DEPENDENCY_ANALYSIS.value: 0.85},
    }


async def correlation(state: InvestigationState) -> dict[str, Any]:
    """Fuse collected evidence into a single time-ordered timeline."""
    events: list[dict] = []
    for dep in state.get("deployments", []):
        events.append({"timestamp": dep["timestamp"], "label": "Deployment",
                       "detail": f"{dep['service']} {dep['version']}: {dep['change_summary']}",
                       "source": "deployment"})
    for alert in state.get("alerts", []):
        events.append({"timestamp": alert["timestamp"], "label": f"Alert: {alert['name']}",
                       "detail": alert["description"], "source": "alert"})
    for log in state.get("logs", []):
        events.append({"timestamp": log["timestamp"], "label": f"Log ({log['source']})",
                       "detail": log["message"], "source": "log"})
    events.sort(key=lambda e: e["timestamp"])
    return {"timeline": events, "confidence_scores": {AgentName.CORRELATION.value: 0.9}}


async def historical_incident(state: InvestigationState) -> dict[str, Any]:
    return {
        "historical_matches": [
            {
                "incident_id": "INC-2025-0421",
                "title": "Auth outage after pool-size change",
                "similarity": 0.91,
                "resolution": "Rolled back deployment; restored DB pool size.",
            }
        ],
        "confidence_scores": {AgentName.HISTORICAL_INCIDENT.value: 0.8},
    }


async def root_cause(state: InvestigationState) -> dict[str, Any]:
    """Rank probable root causes from the correlated evidence."""
    deployments = state.get("deployments", [])
    metrics = state.get("metrics", [])
    db_exhausted = any(
        m.get("metric") == "db_connections" and m.get("value", 0) >= 100 for m in metrics
    )

    candidates: list[dict] = []
    if deployments and db_exhausted:
        candidates.append({
            "category": RootCauseCategory.BAD_DEPLOYMENT.value,
            "title": "Deployment reduced DB pool size, exhausting connections",
            "reasoning": "A deployment 5 minutes before onset reduced the connection pool "
            "and added a synchronous DB write on the login path; connections then "
            "saturated at 100, producing HTTP 500s.",
            "confidence": 0.86,
            "evidence": [
                {"description": "Deployment v2.4.0 at 08:55, 5m before onset", "source": "deployment", "weight": 1.0},
                {"description": "db_connections pinned at 100", "source": "metrics", "weight": 0.9},
            ],
            "supporting_logs": ["QueuePool limit reached", "too many clients"],
            "supporting_metrics": ["db_connections=100", "latency=4200ms"],
        })
        candidates.append({
            "category": RootCauseCategory.CONNECTION_POOL_EXHAUSTION.value,
            "title": "Connection pool exhaustion",
            "reasoning": "Independent of cause, the pool is saturated.",
            "confidence": 0.62,
            "evidence": [{"description": "QueuePool limit reached", "source": "logs", "weight": 0.8}],
            "supporting_logs": ["QueuePool limit reached"],
            "supporting_metrics": ["db_connections=100"],
        })
    else:
        candidates.append({
            "category": RootCauseCategory.UNKNOWN.value,
            "title": "Insufficient evidence for a confident root cause",
            "reasoning": "No correlating deployment or saturation signal was found.",
            "confidence": 0.3,
            "evidence": [],
            "supporting_logs": [],
            "supporting_metrics": [],
        })

    top = max(candidates, key=lambda c: c["confidence"])
    return {
        "root_cause_candidates": candidates,
        "confidence_scores": {AgentName.ROOT_CAUSE.value: top["confidence"]},
    }


async def reflection(state: InvestigationState) -> dict[str, Any]:
    """Critique findings; flag gaps that should trigger a re-plan."""
    passes = state.get("reflection_passes", 0) + 1
    candidates = state.get("root_cause_candidates", [])
    top_conf = max((c["confidence"] for c in candidates), default=0.0)

    gaps: list[str] = []
    if top_conf < 0.5:
        gaps.append("Top root-cause confidence is below 0.5; gather more evidence.")

    return {
        "reflection_gaps": gaps,
        "reflection_passes": passes,
        "confidence_scores": {AgentName.REFLECTION.value: top_conf},
    }


async def recommendation(state: InvestigationState) -> dict[str, Any]:
    """Map the leading root cause to prioritized remediation."""
    candidates = state.get("root_cause_candidates", [])
    top = max(candidates, key=lambda c: c["confidence"], default=None)

    recs: list[dict] = []
    if top and top["category"] == RootCauseCategory.BAD_DEPLOYMENT.value:
        recs.append({
            "action": RemediationAction.ROLLBACK_DEPLOYMENT.value,
            "title": "Roll back auth-api to v2.3.x",
            "justification": "The v2.4.0 deployment introduced the pool reduction that "
            "triggered the outage; rollback is the fastest safe mitigation.",
            "priority": RecommendationPriority.P0.value,
            "risk": RiskLevel.MEDIUM.value,
            "confidence": 0.85,
            "requires_approval": True,
        })
        recs.append({
            "action": RemediationAction.INCREASE_CONNECTION_POOL.value,
            "title": "Temporarily raise the DB connection pool ceiling",
            "justification": "Relieves saturation while the rollback propagates.",
            "priority": RecommendationPriority.P1.value,
            "risk": RiskLevel.LOW.value,
            "confidence": 0.7,
            "requires_approval": True,
        })
    else:
        recs.append({
            "action": RemediationAction.ESCALATE_TO_TEAM.value,
            "title": "Escalate to the on-call SRE team",
            "justification": "Automated analysis could not reach a confident root cause.",
            "priority": RecommendationPriority.P1.value,
            "risk": RiskLevel.LOW.value,
            "confidence": 0.5,
            "requires_approval": False,
        })

    return {"recommendations": recs, "confidence_scores": {AgentName.RECOMMENDATION.value: 0.8}}


async def incident_report(state: InvestigationState) -> dict[str, Any]:
    """Assemble a Markdown incident report from the accumulated state."""
    candidates = state.get("root_cause_candidates", [])
    top = max(candidates, key=lambda c: c["confidence"], default=None)
    recs = state.get("recommendations", [])

    lines = [
        f"# Incident Report — {state.get('incident_id', 'unknown')}",
        "",
        "## Summary",
        state.get("incident_description", ""),
        "",
        "## Probable Root Cause",
        (f"**{top['title']}** (confidence {top['confidence']:.0%})\n\n{top['reasoning']}"
         if top else "Undetermined."),
        "",
        "## Timeline",
    ]
    lines += [f"- `{e['timestamp']}` **{e['label']}** — {e['detail']}"
              for e in state.get("timeline", [])]
    lines += ["", "## Recommendations"]
    lines += [f"- [{r['priority'].upper()}] {r['title']} — {r['justification']}" for r in recs]

    content = "\n".join(lines)
    return {
        "reports": [{"format": "markdown", "title": "Incident Report", "content": content}],
        "confidence_scores": {AgentName.INCIDENT_REPORT.value: 0.9},
    }


async def notification(state: InvestigationState) -> dict[str, Any]:
    """Draft a stakeholder notification."""
    top = max(state.get("root_cause_candidates", []), key=lambda c: c["confidence"], default=None)
    summary = top["title"] if top else "under investigation"
    return {
        "notifications": [
            {
                "channel": "slack",
                "audience": "#incidents",
                "message": f"Investigation for {state.get('incident_id')} complete. "
                f"Probable cause: {summary}. Awaiting/So far approved remediation applied.",
            }
        ],
        "confidence_scores": {AgentName.NOTIFICATION.value: 1.0},
    }


def build_baseline_registry() -> NodeRegistry:
    """Return the instrumented deterministic baseline node registry."""
    return build_registry(
        {
            AgentName.SUPERVISOR: supervisor,
            AgentName.PLANNER: planner,
            AgentName.ALERT_ANALYSIS: alert_analysis,
            AgentName.LOG_ANALYSIS: log_analysis,
            AgentName.METRICS_ANALYSIS: metrics_analysis,
            AgentName.DEPLOYMENT_ANALYSIS: deployment_analysis,
            AgentName.DEPENDENCY_ANALYSIS: dependency_analysis,
            AgentName.CORRELATION: correlation,
            AgentName.HISTORICAL_INCIDENT: historical_incident,
            AgentName.ROOT_CAUSE: root_cause,
            AgentName.REFLECTION: reflection,
            AgentName.RECOMMENDATION: recommendation,
            AgentName.INCIDENT_REPORT: incident_report,
            AgentName.NOTIFICATION: notification,
        }
    )
