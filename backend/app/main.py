"""FastAPI application factory and composition root.

Wires logging, middleware, exception handlers, and routers. Feature routers and the agent
graph are mounted in later phases; the structure here is stable.
"""

from __future__ import annotations

import os
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.api.v1.routes.health import router as health_router
from app.config.logging import configure_logging, get_logger
from app.config.settings import Settings, get_settings
from app.database.session import get_engine, get_sessionmaker
from app.middleware.correlation import CorrelationIdMiddleware
from app.middleware.error_handlers import register_exception_handlers
from app.models import Base
from app.repositories.user_repository import SqlAlchemyUserRepository
from app.services.user_service import UserService

logger = get_logger(__name__)


async def _seed_admin(settings: Settings) -> None:
    """Idempotently create a bootstrap admin from env vars, if configured."""
    email = os.getenv("BOOTSTRAP_ADMIN_EMAIL")
    password = os.getenv("BOOTSTRAP_ADMIN_PASSWORD")
    if not email or not password:
        return
    async with get_sessionmaker()() as session:
        service = UserService(SqlAlchemyUserRepository(session))
        created = await service.ensure_default_admin(
            email=email, full_name="Bootstrap Admin", password=password
        )
        if created:
            await session.commit()
            logger.info("bootstrap.admin_seeded", extra={"email": email})


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    configure_logging(
        level="DEBUG" if settings.app_debug else "INFO",
        json_output=settings.is_production,
    )
    logger.info("app.startup", extra={"env": settings.app_env})

    # In non-production, ensure the schema exists for a frictionless first run.
    # Production relies on Alembic migrations instead.
    if not settings.is_production:
        try:
            engine = get_engine()
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
        except Exception as exc:  # pragma: no cover - startup resilience path
            logger.warning("app.schema_init_failed", extra={"error": str(exc)})

    await _seed_admin(settings)
    yield
    logger.info("app.shutdown")


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        description="Autonomous Incident Response Engineer",
        lifespan=lifespan,
    )

    app.add_middleware(CorrelationIdMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.backend_cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    register_exception_handlers(app)

    app.include_router(health_router)
    app.include_router(api_router, prefix=settings.api_v1_prefix)
    return app


app = create_app()
