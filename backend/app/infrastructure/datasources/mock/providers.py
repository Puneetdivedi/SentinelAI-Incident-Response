"""Mock data-source providers.

Deterministic in-memory fixtures modeling the reference incident across log sources,
metric families, deployments, historical incidents, and a small knowledge base. Filtering
is simple but real (substring/service match, keyword-overlap similarity) so tools exercise
genuine query paths, not hard-coded returns.
"""

from __future__ import annotations

from app.infrastructure.datasources.interfaces import (
    DeploymentProvider,
    IncidentProvider,
    LogProvider,
    MetricsProvider,
    VectorSearchProvider,
)

_T0 = "2026-07-14T09:00:00+00:00"
_T_DEPLOY = "2026-07-14T08:55:00+00:00"

_LOGS: list[dict] = [
    {"timestamp": _T0, "source": "fastapi", "level": "ERROR", "service": "auth-api",
     "message": "HTTP 500 on POST /login: QueuePool limit reached, connection timed out."},
    {"timestamp": _T0, "source": "postgresql", "level": "WARNING", "service": "postgres",
     "message": "remaining connection slots are reserved; too many clients already."},
    {"timestamp": _T0, "source": "kubernetes", "level": "WARNING", "service": "auth-api",
     "message": "Liveness probe failed: HTTP 500; pod auth-api-7c9 restarting."},
    {"timestamp": _T0, "source": "nginx", "level": "ERROR", "service": "gateway",
     "message": "upstream timed out (110: Connection timed out) while reading response from auth-api."},
    {"timestamp": "2026-07-14T08:50:00+00:00", "source": "fastapi", "level": "INFO",
     "service": "auth-api", "message": "Login latency p95 = 120ms (nominal)."},
]

_METRICS: dict[str, list[dict]] = {
    "cpu": [{"timestamp": _T0, "metric": "cpu", "value": 92.0, "unit": "%", "service": "auth-api"}],
    "memory": [{"timestamp": _T0, "metric": "memory", "value": 87.0, "unit": "%", "service": "auth-api"}],
    "latency": [{"timestamp": _T0, "metric": "latency", "value": 4200.0, "unit": "ms", "service": "auth-api"}],
    "error_rate": [{"timestamp": _T0, "metric": "error_rate", "value": 0.23, "unit": "ratio", "service": "auth-api"}],
    "db_connections": [{"timestamp": _T0, "metric": "db_connections", "value": 100.0, "unit": "count", "service": "postgres"}],
}

_DEPLOYMENTS: list[dict] = [
    {"timestamp": _T_DEPLOY, "service": "auth-api", "version": "v2.4.0", "author": "release-bot",
     "change_summary": "Reduced DB pool size; added synchronous audit write on login.",
     "rollback_available": True},
    {"timestamp": "2026-07-13T14:00:00+00:00", "service": "auth-api", "version": "v2.3.1",
     "author": "release-bot", "change_summary": "Dependency bumps.", "rollback_available": True},
]

_INCIDENTS: list[dict] = [
    {"incident_id": "INC-2025-0421", "title": "Auth outage after pool-size change",
     "keywords": ["auth", "login", "pool", "connections", "deployment", "500"],
     "resolution": "Rolled back deployment; restored DB pool size."},
    {"incident_id": "INC-2025-0388", "title": "Redis latency spike",
     "keywords": ["redis", "cache", "latency", "timeout"],
     "resolution": "Increased Redis connection pool; added circuit breaker."},
]

_KB: list[dict] = [
    {"id": "kb-pool", "title": "Diagnosing connection pool exhaustion",
     "keywords": ["pool", "connections", "queuepool", "database", "exhaustion", "login"],
     "content": "QueuePool limit errors indicate the app opened more DB connections than the "
     "pool allows. Check recent pool-size config changes and long-held transactions."},
    {"id": "kb-rollback", "title": "Safe deployment rollback",
     "keywords": ["rollback", "deployment", "release", "revert"],
     "content": "Roll back to the last known-good version when a deployment correlates with "
     "an incident onset and a rollback artifact is available."},
    {"id": "kb-redis", "title": "Redis timeout troubleshooting",
     "keywords": ["redis", "timeout", "cache", "latency"],
     "content": "Redis timeouts often stem from connection saturation or slow commands."},
]


def _keyword_overlap(query: str, keywords: list[str]) -> float:
    terms = {t for t in query.lower().replace("/", " ").split() if len(t) > 2}
    if not terms:
        return 0.0
    hits = sum(1 for k in keywords if k in terms or any(k in t for t in terms))
    return round(hits / max(len(keywords), 1), 3)


class MockLogProvider(LogProvider):
    async def search(self, *, query: str, service: str | None = None, limit: int = 50) -> list[dict]:
        q = query.lower()
        results = [
            entry for entry in _LOGS
            if (service is None or entry["service"] == service)
            and (not q or any(term in entry["message"].lower() for term in q.split()))
        ]
        return results[:limit]


class MockMetricsProvider(MetricsProvider):
    async def query(self, *, metric: str, service: str | None = None) -> list[dict]:
        points = _METRICS.get(metric.lower(), [])
        if service is not None:
            points = [p for p in points if p["service"] == service]
        return list(points)


class MockDeploymentProvider(DeploymentProvider):
    async def history(self, *, service: str | None = None, limit: int = 20) -> list[dict]:
        results = [d for d in _DEPLOYMENTS if service is None or d["service"] == service]
        results = sorted(results, key=lambda d: d["timestamp"], reverse=True)
        return results[:limit]


class MockIncidentProvider(IncidentProvider):
    async def search(self, *, query: str, limit: int = 10) -> list[dict]:
        scored = [
            {**inc, "similarity": _keyword_overlap(query, inc["keywords"])}
            for inc in _INCIDENTS
        ]
        scored = [s for s in scored if s["similarity"] > 0]
        scored.sort(key=lambda s: s["similarity"], reverse=True)
        return [{k: v for k, v in s.items() if k != "keywords"} for s in scored[:limit]]


class MockVectorSearchProvider(VectorSearchProvider):
    async def similarity_search(self, *, query: str, k: int = 5) -> list[dict]:
        scored = [
            {"id": doc["id"], "title": doc["title"], "content": doc["content"],
             "score": _keyword_overlap(query, doc["keywords"])}
            for doc in _KB
        ]
        scored.sort(key=lambda s: s["score"], reverse=True)
        return scored[:k]
