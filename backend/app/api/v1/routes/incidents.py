"""Incident routes and investigation kickoff."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from app.api.deps import CurrentUser, InvestigationServiceDep, require_sre
from app.schemas.incident import (
    IncidentCreate,
    IncidentRead,
    InvestigateRequest,
    InvestigationDetail,
)

router = APIRouter(prefix="/incidents", tags=["incidents"])


@router.post(
    "",
    response_model=IncidentRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_sre)],
)
async def create_incident(
    payload: IncidentCreate, service: InvestigationServiceDep, user: CurrentUser
) -> IncidentRead:
    incident = await service.create_incident(
        title=payload.title,
        description=payload.description,
        severity=payload.severity,
        affected_service=payload.affected_service,
        actor_id=user.id,
    )
    return IncidentRead.model_validate(incident)


@router.get("", response_model=list[IncidentRead])
async def list_incidents(
    service: InvestigationServiceDep,
    _user: CurrentUser,
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> list[IncidentRead]:
    incidents = await service.list_incidents(limit=limit, offset=offset)
    return [IncidentRead.model_validate(i) for i in incidents]


@router.get("/{incident_id}", response_model=IncidentRead)
async def get_incident(
    incident_id: str, service: InvestigationServiceDep, _user: CurrentUser
) -> IncidentRead:
    incident = await service.get_incident(incident_id)
    return IncidentRead.model_validate(incident)


@router.post(
    "/{incident_id}/investigate",
    response_model=InvestigationDetail,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_sre)],
)
async def investigate(
    incident_id: str,
    _payload: InvestigateRequest,
    service: InvestigationServiceDep,
    user: CurrentUser,
) -> InvestigationDetail:
    """Run an autonomous investigation; returns the state paused at human approval."""
    return await service.start_investigation(incident_id=incident_id, actor_id=user.id)
