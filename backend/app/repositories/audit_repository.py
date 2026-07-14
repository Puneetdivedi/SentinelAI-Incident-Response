"""SQLAlchemy implementation of the audit-log repository."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities import AuditEntry
from app.models.audit_log import AuditLogModel
from app.repositories.interfaces import AuditLogRepository


def _to_entity(row: AuditLogModel) -> AuditEntry:
    return AuditEntry(
        id=row.id,
        actor_id=row.actor_id,
        action=row.action,
        resource_type=row.resource_type,
        resource_id=row.resource_id,
        detail=row.detail,
        ip_address=row.ip_address,
        created_at=row.created_at,
    )


class SqlAlchemyAuditLogRepository(AuditLogRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def record(self, entry: AuditEntry) -> AuditEntry:
        row = AuditLogModel(
            actor_id=entry.actor_id,
            action=entry.action,
            resource_type=entry.resource_type,
            resource_id=entry.resource_id,
            detail=entry.detail,
            ip_address=entry.ip_address,
        )
        self._session.add(row)
        await self._session.flush()
        await self._session.refresh(row)
        return _to_entity(row)

    async def list(self, *, limit: int = 100, offset: int = 0) -> list[AuditEntry]:
        result = await self._session.execute(
            select(AuditLogModel)
            .order_by(AuditLogModel.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return [_to_entity(row) for row in result.scalars().all()]
