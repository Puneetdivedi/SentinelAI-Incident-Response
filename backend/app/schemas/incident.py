"""Incident and investigation request/response schemas."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from app.domain.enums import (
    ApprovalStatus,
    IncidentSeverity,
    IncidentStatus,
    InvestigationStatus,
)
from app.schemas.common import ORMModel


class IncidentCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str = Field(min_length=1)
    severity: IncidentSeverity = IncidentSeverity.SEV3
    affected_service: str | None = Field(default=None, max_length=255)


class IncidentRead(ORMModel):
    id: str
    title: str
    description: str
    severity: IncidentSeverity
    status: IncidentStatus
    affected_service: str | None
    created_by: str | None
    created_at: datetime


class InvestigateRequest(BaseModel):
    """Optional free-text prompt to steer the investigation."""

    prompt: str | None = Field(default=None, max_length=2000)


class ApprovalRequest(BaseModel):
    approved: bool
    note: str | None = Field(default=None, max_length=2000)


class ReportRead(ORMModel):
    id: str
    format: str
    title: str
    content: str
    created_at: datetime


class InvestigationSummary(ORMModel):
    id: str
    incident_id: str
    status: InvestigationStatus
    approval_status: ApprovalStatus
    created_at: datetime
    completed_at: datetime | None


class InvestigationDetail(BaseModel):
    id: str
    incident_id: str
    status: InvestigationStatus
    approval_status: ApprovalStatus
    execution_plan: list[str]
    logs: list[dict]
    alerts: list[dict]
    metrics: list[dict]
    deployments: list[dict]
    dependencies: list[dict]
    timeline: list[dict]
    historical_match_ids: list[str]
    root_cause_candidates: list[dict]
    recommendations: list[dict]
    reports: list[ReportRead]
    confidence_scores: dict[str, float]
    errors: list[dict]
    langfuse_trace_id: str | None
    langfuse_session_id: str | None
    created_at: datetime
    completed_at: datetime | None
