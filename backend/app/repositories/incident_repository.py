"""SQLAlchemy implementation of the incident repository."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.enums import IncidentSeverity, IncidentStatus
from app.domain.exceptions import EntityNotFoundError
from app.models.incident import IncidentModel
from app.repositories.interfaces import IncidentRepository


class SqlAlchemyIncidentRepository(IncidentRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(
        self,
        *,
        title: str,
        description: str,
        severity: IncidentSeverity,
        affected_service: str | None,
        created_by: str | None,
    ) -> IncidentModel:
        row = IncidentModel(
            title=title,
            description=description,
            severity=severity,
            affected_service=affected_service,
            created_by=created_by,
        )
        self._session.add(row)
        await self._session.flush()
        await self._session.refresh(row)
        return row

    async def get(self, incident_id: str) -> IncidentModel | None:
        return await self._session.get(IncidentModel, incident_id)

    async def list(self, *, limit: int = 50, offset: int = 0) -> list[IncidentModel]:
        result = await self._session.execute(
            select(IncidentModel)
            .order_by(IncidentModel.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())

    async def set_status(self, incident_id: str, status: IncidentStatus) -> IncidentModel:
        row = await self._session.get(IncidentModel, incident_id)
        if row is None:
            raise EntityNotFoundError(f"Incident '{incident_id}' not found.")
        row.status = status
        await self._session.flush()
        await self._session.refresh(row)
        return row
