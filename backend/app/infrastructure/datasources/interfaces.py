"""Data-source provider interfaces (ports).

Tools depend on these abstractions, never on concrete backends. Mock implementations ship
first; real providers (Loki, Prometheus, ArgoCD, a vector DB, …) implement the same
interfaces and drop in without touching tool or agent code.
"""

from __future__ import annotations

from abc import ABC, abstractmethod


class LogProvider(ABC):
    @abstractmethod
    async def search(
        self, *, query: str, service: str | None = None, limit: int = 50
    ) -> list[dict]:
        """Return log entries matching ``query`` (and optional ``service``)."""


class MetricsProvider(ABC):
    @abstractmethod
    async def query(
        self, *, metric: str, service: str | None = None
    ) -> list[dict]:
        """Return time-series points for a metric family."""


class DeploymentProvider(ABC):
    @abstractmethod
    async def history(self, *, service: str | None = None, limit: int = 20) -> list[dict]:
        """Return recent deployments, newest first."""


class IncidentProvider(ABC):
    @abstractmethod
    async def search(self, *, query: str, limit: int = 10) -> list[dict]:
        """Return historical incidents relevant to ``query``."""


class VectorSearchProvider(ABC):
    @abstractmethod
    async def similarity_search(self, *, query: str, k: int = 5) -> list[dict]:
        """Return the ``k`` most similar knowledge-base entries with scores."""
