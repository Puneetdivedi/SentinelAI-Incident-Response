"""Dependency-injection container.

A single composition root that constructs and caches long-lived collaborators (settings,
engine, session factory). Later phases register repositories, services, the LLM client,
and the agent graph here so nothing is constructed inside routes.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from app.config.settings import Settings, get_settings
from app.database.session import get_engine, get_sessionmaker


@dataclass
class Container:
    """Application composition root.

    Holds process-wide singletons. Request-scoped objects (like ``AsyncSession``) are
    produced on demand via factories rather than stored on the container.
    """

    settings: Settings = field(default_factory=get_settings)

    @property
    def engine(self) -> AsyncEngine:
        return get_engine()

    @property
    def session_factory(self) -> async_sessionmaker[AsyncSession]:
        return get_sessionmaker()


_container: Container | None = None


def get_container() -> Container:
    """Return the process-wide container singleton."""
    global _container
    if _container is None:
        _container = Container()
    return _container


def reset_container() -> None:
    """Reset the container (used by tests to inject overrides)."""
    global _container
    _container = None
