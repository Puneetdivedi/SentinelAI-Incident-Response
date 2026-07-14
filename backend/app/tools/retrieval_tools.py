"""Retrieval tools backed by data-source providers."""

from __future__ import annotations

from pydantic import BaseModel, Field

from app.infrastructure.datasources.interfaces import (
    DeploymentProvider,
    IncidentProvider,
    LogProvider,
    MetricsProvider,
    VectorSearchProvider,
)
from app.tools.base import BaseTool


class LogSearchInput(BaseModel):
    query: str = Field(description="Keywords to search log messages for.")
    service: str | None = Field(default=None, description="Optional service filter.")
    limit: int = Field(default=50, ge=1, le=500)


class LogSearchTool(BaseTool):
    name = "log_search"
    description = "Search application/infrastructure logs by keyword and optional service."
    args_schema = LogSearchInput

    def __init__(self, provider: LogProvider) -> None:
        self._provider = provider

    async def arun(self, *, query: str, service: str | None = None, limit: int = 50) -> list[dict]:
        return await self._provider.search(query=query, service=service, limit=limit)


class MetricsQueryInput(BaseModel):
    metric: str = Field(description="Metric family: cpu|memory|latency|error_rate|db_connections.")
    service: str | None = Field(default=None)


class MetricsQueryTool(BaseTool):
    name = "metrics_query"
    description = "Query a time-series metric family for the incident window."
    args_schema = MetricsQueryInput

    def __init__(self, provider: MetricsProvider) -> None:
        self._provider = provider

    async def arun(self, *, metric: str, service: str | None = None) -> list[dict]:
        return await self._provider.query(metric=metric, service=service)


class DeploymentHistoryInput(BaseModel):
    service: str | None = Field(default=None)
    limit: int = Field(default=20, ge=1, le=100)


class DeploymentHistoryTool(BaseTool):
    name = "deployment_history"
    description = "List recent deployments (newest first), optionally filtered by service."
    args_schema = DeploymentHistoryInput

    def __init__(self, provider: DeploymentProvider) -> None:
        self._provider = provider

    async def arun(self, *, service: str | None = None, limit: int = 20) -> list[dict]:
        return await self._provider.history(service=service, limit=limit)


class IncidentSearchInput(BaseModel):
    query: str = Field(description="Description of the current incident to match against history.")
    limit: int = Field(default=10, ge=1, le=50)


class IncidentSearchTool(BaseTool):
    name = "incident_search"
    description = "Find historical incidents similar to the current one."
    args_schema = IncidentSearchInput

    def __init__(self, provider: IncidentProvider) -> None:
        self._provider = provider

    async def arun(self, *, query: str, limit: int = 10) -> list[dict]:
        return await self._provider.search(query=query, limit=limit)


class VectorSearchInput(BaseModel):
    query: str = Field(description="Natural-language query for the knowledge base.")
    k: int = Field(default=5, ge=1, le=20)


class VectorSearchTool(BaseTool):
    name = "vector_search"
    description = "Semantic search over the incident-response knowledge base."
    args_schema = VectorSearchInput

    def __init__(self, provider: VectorSearchProvider) -> None:
        self._provider = provider

    async def arun(self, *, query: str, k: int = 5) -> list[dict]:
        return await self._provider.similarity_search(query=query, k=k)
