"""Domain value objects.

Immutable, equality-by-value objects with self-validating invariants. These carry no
persistence or framework concerns and are safe to use inside the agent graph state.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from app.domain.enums import (
    LogSource,
    MetricType,
    RecommendationPriority,
    RemediationAction,
    RiskLevel,
    RootCauseCategory,
)
from app.domain.exceptions import ValidationError


@dataclass(frozen=True, slots=True)
class ConfidenceScore:
    """A bounded [0.0, 1.0] confidence value produced by an agent."""

    value: float

    def __post_init__(self) -> None:
        if not 0.0 <= self.value <= 1.0:
            raise ValidationError(
                f"ConfidenceScore must be within [0.0, 1.0], got {self.value}."
            )

    @property
    def percent(self) -> int:
        return round(self.value * 100)


@dataclass(frozen=True, slots=True)
class LogEntry:
    """A single normalized log line from any source."""

    timestamp: datetime
    source: LogSource
    level: str
    message: str
    service: str | None = None
    trace_id: str | None = None


@dataclass(frozen=True, slots=True)
class MetricPoint:
    """A single time-series sample."""

    timestamp: datetime
    metric: MetricType
    value: float
    unit: str
    service: str | None = None


@dataclass(frozen=True, slots=True)
class Alert:
    """A monitoring alert firing during the incident window."""

    timestamp: datetime
    name: str
    severity: str
    description: str
    service: str | None = None


@dataclass(frozen=True, slots=True)
class Deployment:
    """A deployment event correlated against the incident timeline."""

    timestamp: datetime
    service: str
    version: str
    author: str
    change_summary: str
    rollback_available: bool = True


@dataclass(frozen=True, slots=True)
class Report:
    """A generated investigation report."""

    id: str
    format: ReportFormat
    title: str
    content: str
    created_at: datetime | None = None


@dataclass(frozen=True, slots=True)
class DependencyStatus:
    """Health snapshot of an upstream/downstream dependency."""

    name: str
    healthy: bool
    latency_ms: float | None = None
    error_rate: float | None = None
    detail: str | None = None


@dataclass(frozen=True, slots=True)
class TimelineEvent:
    """A single event on the reconstructed incident timeline."""

    timestamp: datetime
    label: str
    detail: str
    source: str


@dataclass(frozen=True, slots=True)
class Evidence:
    """A discrete piece of supporting evidence attached to a hypothesis."""

    description: str
    source: str
    weight: float = 1.0

    def __post_init__(self) -> None:
        if self.weight < 0:
            raise ValidationError("Evidence weight must be non-negative.")


@dataclass(frozen=True, slots=True)
class RootCauseHypothesis:
    """A ranked root-cause hypothesis with its supporting evidence."""

    category: RootCauseCategory
    title: str
    reasoning: str
    confidence: ConfidenceScore
    evidence: tuple[Evidence, ...] = field(default_factory=tuple)
    supporting_logs: tuple[str, ...] = field(default_factory=tuple)
    supporting_metrics: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True, slots=True)
class Recommendation:
    """A prioritized remediation with risk and justification."""

    action: RemediationAction
    title: str
    justification: str
    priority: RecommendationPriority
    risk: RiskLevel
    confidence: ConfidenceScore
    requires_approval: bool = True
