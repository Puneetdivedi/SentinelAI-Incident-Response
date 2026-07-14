"""Audit service — records security-relevant actions."""

from __future__ import annotations

from app.config.logging import get_logger
from app.domain.entities import AuditEntry
from app.repositories.interfaces import AuditLogRepository

logger = get_logger(__name__)


class AuditService:
    def __init__(self, audit_repository: AuditLogRepository) -> None:
        self._repo = audit_repository

    async def record(
        self,
        *,
        action: str,
        resource_type: str,
        actor_id: str | None = None,
        resource_id: str | None = None,
        detail: str | None = None,
        ip_address: str | None = None,
    ) -> None:
        entry = AuditEntry(
            id="",  # assigned by the repository/DB
            actor_id=actor_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            detail=detail,
            ip_address=ip_address,
        )
        await self._repo.record(entry)
        logger.info(
            "audit",
            extra={
                "audit_action": action,
                "resource_type": resource_type,
                "actor_id": actor_id,
                "resource_id": resource_id,
            },
        )
