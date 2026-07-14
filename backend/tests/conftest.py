"""Shared pytest fixtures.

Runs the full app against an in-memory SQLite database (shared via StaticPool) with the
``get_session`` dependency overridden, so the API and persistence layers are exercised
end-to-end without Postgres, Redis, or any external service.
"""

from __future__ import annotations

from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.database.session import get_session
from app.domain.enums import UserRole
from app.main import create_app
from app.models import Base
from app.repositories.user_repository import SqlAlchemyUserRepository
from app.services.user_service import UserService

ADMIN_EMAIL = "admin@sentinel.ai"
ADMIN_PASSWORD = "admin-password-123"
VIEWER_EMAIL = "viewer@sentinel.ai"
VIEWER_PASSWORD = "viewer-password-123"


@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    session_factory = async_sessionmaker(engine, expire_on_commit=False, autoflush=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Seed an admin and a viewer.
    async with session_factory() as session:
        service = UserService(SqlAlchemyUserRepository(session))
        await service.create_user(
            email=ADMIN_EMAIL,
            full_name="Admin",
            password=ADMIN_PASSWORD,
            role=UserRole.ADMIN,
        )
        await service.create_user(
            email=VIEWER_EMAIL,
            full_name="Viewer",
            password=VIEWER_PASSWORD,
            role=UserRole.VIEWER,
        )
        await session.commit()

    async def _override_session() -> AsyncGenerator:
        async with session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    app = create_app()
    app.dependency_overrides[get_session] = _override_session

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()
    await engine.dispose()


async def _login(client: AsyncClient, email: str, password: str) -> str:
    resp = await client.post(
        "/api/v1/auth/login", json={"email": email, "password": password}
    )
    assert resp.status_code == 200, resp.text
    return resp.json()["access_token"]


@pytest.fixture
async def admin_token(client: AsyncClient) -> str:
    return await _login(client, ADMIN_EMAIL, ADMIN_PASSWORD)


@pytest.fixture
async def viewer_token(client: AsyncClient) -> str:
    return await _login(client, VIEWER_EMAIL, VIEWER_PASSWORD)
