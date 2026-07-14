"""Repository interfaces (ports).

The application/service layer depends only on these abstractions. SQLAlchemy
implementations live alongside; tests or future providers can substitute fakes.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from app.domain.entities import AuditEntry, User
from app.domain.enums import UserRole


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
