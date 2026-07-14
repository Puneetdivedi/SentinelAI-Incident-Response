"""SQLAlchemy implementation of the user repository."""

from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities import User
from app.domain.enums import UserRole
from app.models.user import UserModel
from app.repositories.interfaces import UserRepository


def _to_entity(row: UserModel) -> User:
    return User(
        id=row.id,
        email=row.email,
        full_name=row.full_name,
        role=row.role,
        hashed_password=row.hashed_password,
        is_active=row.is_active,
        created_at=row.created_at,
    )


class SqlAlchemyUserRepository(UserRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, user_id: str) -> User | None:
        row = await self._session.get(UserModel, user_id)
        return _to_entity(row) if row else None

    async def get_by_email(self, email: str) -> User | None:
        result = await self._session.execute(
            select(UserModel).where(UserModel.email == email)
        )
        row = result.scalar_one_or_none()
        return _to_entity(row) if row else None

    async def list(self, *, limit: int = 100, offset: int = 0) -> list[User]:
        result = await self._session.execute(
            select(UserModel)
            .order_by(UserModel.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return [_to_entity(row) for row in result.scalars().all()]

    async def create(
        self,
        *,
        email: str,
        full_name: str,
        hashed_password: str,
        role: UserRole,
    ) -> User:
        row = UserModel(
            email=email,
            full_name=full_name,
            hashed_password=hashed_password,
            role=role,
        )
        self._session.add(row)
        await self._session.flush()
        await self._session.refresh(row)
        return _to_entity(row)

    async def update(self, user: User) -> User:
        row = await self._session.get(UserModel, user.id)
        if row is None:
            raise ValueError(f"User {user.id} not found for update.")
        row.full_name = user.full_name
        row.hashed_password = user.hashed_password
        row.role = user.role
        row.is_active = user.is_active
        await self._session.flush()
        await self._session.refresh(row)
        return _to_entity(row)

    async def count(self) -> int:
        result = await self._session.execute(select(func.count()).select_from(UserModel))
        return int(result.scalar_one())
