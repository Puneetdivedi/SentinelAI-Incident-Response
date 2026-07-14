"""Assemble the platform toolset from data-source providers.

Defaults to the mock providers so the toolset works offline; real providers are injected
in production. The SQL tool is included only when a DB session factory is supplied.
"""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.infrastructure.datasources.interfaces import (
    DeploymentProvider,
    IncidentProvider,
    LogProvider,
    MetricsProvider,
    VectorSearchProvider,
)
from app.infrastructure.datasources.mock.providers import (
    MockDeploymentProvider,
    MockIncidentProvider,
    MockLogProvider,
    MockMetricsProvider,
    MockVectorSearchProvider,
)
from app.tools.analysis_tools import PythonExecutionTool, SqlQueryTool
from app.tools.base import BaseTool
from app.tools.report_tools import (
    ChartGenerationTool,
    MarkdownReportTool,
    NotificationGeneratorTool,
    PdfReportTool,
    TimelineGeneratorTool,
    WordReportTool,
)
from app.tools.retrieval_tools import (
    DeploymentHistoryTool,
    IncidentSearchTool,
    LogSearchTool,
    MetricsQueryTool,
    VectorSearchTool,
)


class DataProviders:
    """Bundle of data-source providers used by the retrieval tools."""

    def __init__(
        self,
        *,
        logs: LogProvider,
        metrics: MetricsProvider,
        deployments: DeploymentProvider,
        incidents: IncidentProvider,
        vectors: VectorSearchProvider,
    ) -> None:
        self.logs = logs
        self.metrics = metrics
        self.deployments = deployments
        self.incidents = incidents
        self.vectors = vectors


def build_mock_providers() -> DataProviders:
    return DataProviders(
        logs=MockLogProvider(),
        metrics=MockMetricsProvider(),
        deployments=MockDeploymentProvider(),
        incidents=MockIncidentProvider(),
        vectors=MockVectorSearchProvider(),
    )


def build_retrieval_tools(providers: DataProviders) -> list[BaseTool]:
    return [
        LogSearchTool(providers.logs),
        MetricsQueryTool(providers.metrics),
        DeploymentHistoryTool(providers.deployments),
        IncidentSearchTool(providers.incidents),
        VectorSearchTool(providers.vectors),
    ]


def build_report_tools() -> list[BaseTool]:
    return [
        MarkdownReportTool(),
        PdfReportTool(),
        WordReportTool(),
        ChartGenerationTool(),
        TimelineGeneratorTool(),
        NotificationGeneratorTool(),
    ]


def build_all_tools(
    *,
    providers: DataProviders | None = None,
    session_factory: async_sessionmaker[AsyncSession] | None = None,
) -> list[BaseTool]:
    """Return the complete toolset. Uses mock providers when none are supplied."""
    providers = providers or build_mock_providers()
    tools: list[BaseTool] = build_retrieval_tools(providers)
    tools.append(PythonExecutionTool())
    if session_factory is not None:
        tools.append(SqlQueryTool(session_factory))
    tools.extend(build_report_tools())
    return tools
