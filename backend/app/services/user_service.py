"""User management service."""

from __future__ import annotations

from app.config.logging import get_logger
from app.domain.entities import User
from app.domain.enums import UserRole
from app.domain.exceptions import DuplicateEntityError, EntityNotFoundError
from app.repositories.interfaces import UserRepository
from app.utils.security import hash_password

logger = get_logger(__name__)


class UserService:
    def __init__(self, user_repository: UserRepository) -> None:
        self._users = user_repository

    async def create_user(
        self, *, email: str, full_name: str, password: str, role: UserRole
    ) -> User:
        if await self._users.get_by_email(email) is not None:
            raise DuplicateEntityError(f"A user with email '{email}' already exists.")
        user = await self._users.create(
            email=email,
            full_name=full_name,
            hashed_password=hash_password(password),
            role=role,
        )
        logger.info("user.created", extra={"user_id": user.id, "role": role.value})
        return user

    async def get_user(self, user_id: str) -> User:
        user = await self._users.get_by_id(user_id)
        if user is None:
            raise EntityNotFoundError(f"User '{user_id}' not found.")
        return user

    async def list_users(self, *, limit: int = 100, offset: int = 0) -> list[User]:
        return await self._users.list(limit=limit, offset=offset)

    async def update_profile(
        self, user_id: str, *, full_name: str | None, password: str | None
    ) -> User:
        user = await self.get_user(user_id)
        if full_name is not None:
            user.full_name = full_name
        if password is not None:
            user.hashed_password = hash_password(password)
        return await self._users.update(user)

    async def change_role(self, user_id: str, role: UserRole) -> User:
        user = await self.get_user(user_id)
        user.role = role
        updated = await self._users.update(user)
        logger.info("user.role_changed", extra={"user_id": user_id, "role": role.value})
        return updated

    async def set_active(self, user_id: str, *, is_active: bool) -> User:
        user = await self.get_user(user_id)
        user.is_active = is_active
        return await self._users.update(user)

    async def ensure_default_admin(
        self, *, email: str, full_name: str, password: str
    ) -> User | None:
        """Idempotently seed a bootstrap admin when the users table is empty."""
        if await self._users.count() > 0:
            return None
        user = await self._users.create(
            email=email,
            full_name=full_name,
            hashed_password=hash_password(password),
            role=UserRole.ADMIN,
        )
        logger.info("user.bootstrap_admin_created", extra={"user_id": user.id})
        return user
