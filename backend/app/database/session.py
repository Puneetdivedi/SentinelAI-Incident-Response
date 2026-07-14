"""Async database engine and session management.

Provides a lazily-constructed async engine + sessionmaker and a FastAPI dependency
``get_session`` that yields a transactional ``AsyncSession`` per request.
"""

from __future__ import annotations

from collections.abc import AsyncGenerator
from functools import lru_cache

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.config.settings import get_settings


@lru_cache
def get_engine() -> AsyncEngine:
    """Return a cached async engine built from settings."""
    settings = get_settings()
    return create_async_engine(
        settings.database_url,
        echo=settings.app_debug and not settings.is_production,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20,
        future=True,
    )


@lru_cache
def get_sessionmaker() -> async_sessionmaker[AsyncSession]:
    """Return a cached async session factory."""
    return async_sessionmaker(
        bind=get_engine(),
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
    )


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency yielding a session inside a transaction.

    Commits on success, rolls back on any exception, and always closes the session.
    """
    session_factory = get_sessionmaker()
    async with session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
