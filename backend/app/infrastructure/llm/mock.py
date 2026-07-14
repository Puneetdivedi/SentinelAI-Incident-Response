"""Deterministic mock LLM provider.

Returns canned, schema-valid fixtures per agent so the entire agent graph runs without API
keys or network — used by tests, CI, and local development (``LLM_PROVIDER=mock``). The
fixtures mirror the reference incident (a pool-reducing deployment causing auth 500s).
"""

from __future__ import annotations

from typing import Any

from app.domain.enums import AgentName
from app.domain.exceptions import LLMError
from app.infrastructure.llm.base import LLMProvider, OutputT

_T0 = "2026-07-14T09:00:00+00:00"
_T_DEPLOY = "2026-07-14T08:55:00+00:00"


def build_default_mock_responses() -> dict[AgentName, dict[str, Any]]:
    """Return a fresh set of canned per-agent responses."""
    return {
        AgentName.SUPERVISOR: {
            "acknowledgement": "Incident acknowledged; investigation starting.",
            "confidence": 1.0,
        },
        AgentName.PLANNER: {
            "steps": [
                "Inspect monitoring alerts",
                "Retrieve and analyze logs",
                "Analyze CPU/memory/latency/DB-connection metrics",
                "Inspect recent deployments",
                "Check dependency health",
                "Correlate evidence into a timeline",
                "Search historical incidents",
                "Determine probable root cause",
                "Recommend remediation",
            ],
            "confidence": 1.0,
        },
        AgentName.ALERT_ANALYSIS: {
            "alerts": [
                {
                    "timestamp": _T0,
                    "name": "HighErrorRate",
                    "severity": "critical",
                    "description": "Auth API 5xx rate above 20% for 5 minutes.",
                    "service": "auth-api",
                }
            ],
            "summary": "A critical error-rate alert fired on auth-api at onset.",
            "confidence": 0.9,
        },
        AgentName.LOG_ANALYSIS: {
            "logs": [
                {
                    "timestamp": _T0,
                    "source": "fastapi",
                    "level": "ERROR",
                    "message": "HTTP 500 on POST /login: QueuePool limit reached, connection timed out.",
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
            "summary": "Login path exhausts the DB connection pool.",
            "confidence": 0.88,
        },
        AgentName.METRICS_ANALYSIS: {
            "metrics": [
                {"timestamp": _T0, "metric": "cpu", "value": 92.0, "unit": "%", "service": "auth-api"},
                {"timestamp": _T0, "metric": "memory", "value": 87.0, "unit": "%", "service": "auth-api"},
                {"timestamp": _T0, "metric": "db_connections", "value": 100.0, "unit": "count", "service": "postgres"},
                {"timestamp": _T0, "metric": "latency", "value": 4200.0, "unit": "ms", "service": "auth-api"},
            ],
            "summary": "DB connections saturated at 100; latency spiked to 4.2s.",
            "confidence": 0.9,
        },
        AgentName.DEPLOYMENT_ANALYSIS: {
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
            "summary": "auth-api v2.4.0 shipped 5 minutes before onset.",
            "confidence": 0.95,
        },
        AgentName.DEPENDENCY_ANALYSIS: {
            "dependencies": [
                {"name": "postgres", "healthy": False, "latency_ms": 3800.0, "error_rate": 0.0,
                 "detail": "Connection pool exhausted."},
                {"name": "redis", "healthy": True, "latency_ms": 3.0, "error_rate": 0.0, "detail": None},
            ],
            "summary": "Postgres unhealthy due to pool exhaustion; Redis nominal.",
            "confidence": 0.85,
        },
        AgentName.CORRELATION: {
            "timeline": [
                {"timestamp": _T_DEPLOY, "label": "Deployment",
                 "detail": "auth-api v2.4.0: reduced DB pool size.", "source": "deployment"},
                {"timestamp": _T0, "label": "Alert: HighErrorRate",
                 "detail": "Auth 5xx above 20%.", "source": "alert"},
                {"timestamp": _T0, "label": "Log (fastapi)",
                 "detail": "QueuePool limit reached on /login.", "source": "log"},
            ],
            "summary": "Deploy precedes the error spike by 5 minutes.",
            "confidence": 0.9,
        },
        AgentName.HISTORICAL_INCIDENT: {
            "matches": [
                {
                    "incident_id": "INC-2025-0421",
                    "title": "Auth outage after pool-size change",
                    "similarity": 0.91,
                    "resolution": "Rolled back deployment; restored DB pool size.",
                }
            ],
            "confidence": 0.8,
        },
        AgentName.ROOT_CAUSE: {
            "candidates": [
                {
                    "category": "bad_deployment",
                    "title": "Deployment reduced DB pool size, exhausting connections",
                    "reasoning": "auth-api v2.4.0 (5m before onset) reduced the pool and added a "
                    "synchronous DB write on login; connections saturated at 100, causing 500s.",
                    "confidence": 0.86,
                    "evidence": [
                        {"description": "Deployment v2.4.0 at 08:55", "source": "deployment", "weight": 1.0},
                        {"description": "db_connections pinned at 100", "source": "metrics", "weight": 0.9},
                    ],
                    "supporting_logs": ["QueuePool limit reached", "too many clients"],
                    "supporting_metrics": ["db_connections=100", "latency=4200ms"],
                },
                {
                    "category": "connection_pool_exhaustion",
                    "title": "Connection pool exhaustion",
                    "reasoning": "The pool is saturated regardless of first cause.",
                    "confidence": 0.62,
                    "evidence": [{"description": "QueuePool limit reached", "source": "logs", "weight": 0.8}],
                    "supporting_logs": ["QueuePool limit reached"],
                    "supporting_metrics": ["db_connections=100"],
                },
            ],
            "confidence": 0.86,
        },
        AgentName.REFLECTION: {"sufficient": True, "gaps": [], "confidence": 0.86},
        AgentName.RECOMMENDATION: {
            "recommendations": [
                {
                    "action": "rollback_deployment",
                    "title": "Roll back auth-api to v2.3.x",
                    "justification": "v2.4.0 introduced the pool reduction that triggered the outage.",
                    "priority": "p0",
                    "risk": "medium",
                    "confidence": 0.85,
                    "requires_approval": True,
                },
                {
                    "action": "increase_connection_pool",
                    "title": "Temporarily raise the DB connection pool ceiling",
                    "justification": "Relieves saturation while the rollback propagates.",
                    "priority": "p1",
                    "risk": "low",
                    "confidence": 0.7,
                    "requires_approval": True,
                },
            ],
            "confidence": 0.85,
        },
        AgentName.INCIDENT_REPORT: {
            "title": "Incident Report — Auth 500s after v2.4.0",
            "content_markdown": (
                "# Incident Report — Auth 500s after v2.4.0\n\n"
                "## Summary\nUsers could not log in; auth-api returned HTTP 500.\n\n"
                "## Probable Root Cause\nDeployment v2.4.0 reduced the DB connection pool and "
                "added a synchronous audit write on login, exhausting connections.\n\n"
                "## Recommendations\n- [P0] Roll back auth-api to v2.3.x\n"
                "- [P1] Temporarily raise the DB connection pool ceiling\n\n"
                "## Lessons Learned\nGate pool-size changes behind load testing.\n"
            ),
            "confidence": 0.9,
        },
        AgentName.NOTIFICATION: {
            "channel": "slack",
            "audience": "#incidents",
            "message": "Auth 500s traced to auth-api v2.4.0 reducing the DB pool. "
            "Recommended remediation: roll back to v2.3.x (awaiting approval).",
            "confidence": 1.0,
        },
    }


class MockLLMProvider(LLMProvider):
    """Returns canned, schema-valid responses keyed by agent."""

    def __init__(self, responses: dict[AgentName, dict[str, Any]] | None = None) -> None:
        self._responses = responses if responses is not None else build_default_mock_responses()

    @property
    def model_name(self) -> str:
        return "mock-llm"

    async def structured_output(
        self,
        *,
        agent: AgentName,
        system_prompt: str,
        user_prompt: str,
        output_model: type[OutputT],
    ) -> OutputT:
        data = self._responses.get(agent)
        if data is None:
            raise LLMError(f"No mock response registered for agent '{agent.value}'.")
        return output_model.model_validate(data)
