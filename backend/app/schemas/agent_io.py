"""Structured-output schemas for every agent.

These are the Pydantic models each agent forces the LLM to return. Keeping them here (rather
than inline in each agent) lets the mock provider build fixtures and the graph map outputs
uniformly. Confidence is a first-class field on every analytical output.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from app.domain.enums import (
    RecommendationPriority,
    RemediationAction,
    RiskLevel,
    RootCauseCategory,
)

Confidence = Field(ge=0.0, le=1.0, description="Agent confidence in [0,1].")


# ── Evidence item schemas ────────────────────────────────────
class AlertItem(BaseModel):
    timestamp: str
    name: str
    severity: str
    description: str
    service: str | None = None


class LogItem(BaseModel):
    timestamp: str
    source: str
    level: str
    message: str
    service: str | None = None


class MetricItem(BaseModel):
    timestamp: str
    metric: str
    value: float
    unit: str
    service: str | None = None


class DeploymentItem(BaseModel):
    timestamp: str
    service: str
    version: str
    author: str
    change_summary: str
    rollback_available: bool = True


class DependencyItem(BaseModel):
    name: str
    healthy: bool
    latency_ms: float | None = None
    error_rate: float | None = None
    detail: str | None = None


class TimelineItem(BaseModel):
    timestamp: str
    label: str
    detail: str
    source: str


class HistoricalMatchItem(BaseModel):
    incident_id: str
    title: str
    similarity: float = Field(ge=0.0, le=1.0)
    resolution: str


class EvidenceItem(BaseModel):
    description: str
    source: str
    weight: float = Field(default=1.0, ge=0.0)


class HypothesisItem(BaseModel):
    category: RootCauseCategory
    title: str
    reasoning: str
    confidence: float = Confidence
    evidence: list[EvidenceItem] = Field(default_factory=list)
    supporting_logs: list[str] = Field(default_factory=list)
    supporting_metrics: list[str] = Field(default_factory=list)


class RecommendationItem(BaseModel):
    action: RemediationAction
    title: str
    justification: str
    priority: RecommendationPriority
    risk: RiskLevel
    confidence: float = Confidence
    requires_approval: bool = True


# ── Per-agent output schemas ─────────────────────────────────
class SupervisorOutput(BaseModel):
    acknowledgement: str
    confidence: float = Confidence


class PlannerOutput(BaseModel):
    steps: list[str] = Field(min_length=1)
    confidence: float = Confidence


class AlertAnalysisOutput(BaseModel):
    alerts: list[AlertItem] = Field(default_factory=list)
    summary: str
    confidence: float = Confidence


class LogAnalysisOutput(BaseModel):
    logs: list[LogItem] = Field(default_factory=list)
    summary: str
    confidence: float = Confidence


class MetricsAnalysisOutput(BaseModel):
    metrics: list[MetricItem] = Field(default_factory=list)
    summary: str
    confidence: float = Confidence


class DeploymentAnalysisOutput(BaseModel):
    deployments: list[DeploymentItem] = Field(default_factory=list)
    summary: str
    confidence: float = Confidence


class DependencyAnalysisOutput(BaseModel):
    dependencies: list[DependencyItem] = Field(default_factory=list)
    summary: str
    confidence: float = Confidence


class CorrelationOutput(BaseModel):
    timeline: list[TimelineItem] = Field(default_factory=list)
    summary: str
    confidence: float = Confidence


class HistoricalOutput(BaseModel):
    matches: list[HistoricalMatchItem] = Field(default_factory=list)
    confidence: float = Confidence


class RootCauseOutput(BaseModel):
    candidates: list[HypothesisItem] = Field(min_length=1)
    confidence: float = Confidence


class ReflectionOutput(BaseModel):
    sufficient: bool
    gaps: list[str] = Field(default_factory=list)
    confidence: float = Confidence


class RecommendationOutput(BaseModel):
    recommendations: list[RecommendationItem] = Field(default_factory=list)
    confidence: float = Confidence


class IncidentReportOutput(BaseModel):
    title: str
    content_markdown: str
    confidence: float = Confidence


class NotificationOutput(BaseModel):
    channel: str
    audience: str
    message: str
    confidence: float = Confidence
