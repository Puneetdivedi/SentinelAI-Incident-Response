"""Repository interfaces (ports).

The application/service layer depends only on these abstractions. SQLAlchemy
implementations live alongside; tests or future providers can substitute fakes.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from app.domain.entities import AuditEntry, User
from app.domain.enums import (
    ApprovalStatus,
    IncidentSeverity,
    IncidentStatus,
    InvestigationStatus,
    UserRole,
)


class UserRepository(ABC):
    """Persistence port for users."""

    @abstractmethod
    async def get_by_id(self, user_id: str) -> User | None: ...

    @abstractmethod
    async def get_by_email(self, email: str) -> User | None: ...

    @abstractmethod
    async def list(self, *, limit: int = 100, offset: int = 0) -> list[User]: ...

    @abstractmethod
    async def create(
        self,
        *,
        email: str,
        full_name: str,
        hashed_password: str,
        role: UserRole,
    ) -> User: ...

    @abstractmethod
    async def update(self, user: User) -> User: ...

    @abstractmethod
    async def count(self) -> int: ...


class AuditLogRepository(ABC):
    """Persistence port for the append-only audit trail."""

    @abstractmethod
    async def record(self, entry: AuditEntry) -> AuditEntry: ...

    @abstractmethod
    async def list(
        self, *, limit: int = 100, offset: int = 0
    ) -> list[AuditEntry]: ...


class IncidentRepository(ABC):
    """Persistence port for incidents. Returns ORM models (JSON-heavy aggregate)."""

    @abstractmethod
    async def create(
        self,
        *,
        title: str,
        description: str,
        severity: IncidentSeverity,
        affected_service: str | None,
        created_by: str | None,
    ) -> Any: ...

    @abstractmethod
    async def get(self, incident_id: str) -> Any | None: ...

    @abstractmethod
    async def list(self, *, limit: int = 50, offset: int = 0) -> list[Any]: ...

    @abstractmethod
    async def set_status(self, incident_id: str, status: IncidentStatus) -> Any: ...


class InvestigationRepository(ABC):
    """Persistence port for investigations and their child records."""

    @abstractmethod
    async def create(self, *, incident_id: str) -> Any: ...

    @abstractmethod
    async def get(self, investigation_id: str) -> Any | None: ...

    @abstractmethod
    async def list(
        self, *, incident_id: str | None = None, limit: int = 50, offset: int = 0
    ) -> list[Any]: ...

    @abstractmethod
    async def save_state(
        self,
        investigation_id: str,
        state: dict,
        *,
        status: InvestigationStatus,
        approval_status: ApprovalStatus,
        completed: bool = False,
        approved_by: str | None = None,
    ) -> Any: ...
