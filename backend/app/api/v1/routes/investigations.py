"""Investigation query and human-approval routes."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.deps import CurrentUser, InvestigationServiceDep, require_sre
from app.schemas.incident import (
    ApprovalRequest,
    InvestigationDetail,
    InvestigationSummary,
    ReportRead,
)

router = APIRouter(prefix="/investigations", tags=["investigations"])


@router.get("", response_model=list[InvestigationSummary])
async def list_investigations(
    service: InvestigationServiceDep,
    _user: CurrentUser,
    incident_id: Annotated[str | None, Query()] = None,
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> list[InvestigationSummary]:
    rows = await service.list_investigations(
        incident_id=incident_id, limit=limit, offset=offset
    )
    return [InvestigationSummary.model_validate(r) for r in rows]


@router.get("/{investigation_id}", response_model=InvestigationDetail)
async def get_investigation(
    investigation_id: str, service: InvestigationServiceDep, _user: CurrentUser
) -> InvestigationDetail:
    return await service.get_investigation(investigation_id)


@router.get("/{investigation_id}/reports", response_model=list[ReportRead])
async def get_reports(
    investigation_id: str, service: InvestigationServiceDep, _user: CurrentUser
) -> list[ReportRead]:
    detail = await service.get_investigation(investigation_id)
    return detail.reports


@router.post(
    "/{investigation_id}/approve",
    response_model=InvestigationDetail,
    dependencies=[Depends(require_sre)],
)
async def approve_investigation(
    investigation_id: str,
    payload: ApprovalRequest,
    service: InvestigationServiceDep,
    user: CurrentUser,
) -> InvestigationDetail:
    """Approve or reject the recommended remediation (Admin/SRE only)."""
    if not user.can_approve:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your role cannot approve remediation.",
        )
    return await service.decide(
        investigation_id=investigation_id,
        approved=payload.approved,
        actor_id=user.id,
        note=payload.note,
    )
