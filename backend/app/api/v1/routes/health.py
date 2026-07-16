"""Liveness/readiness endpoints."""

from __future__ import annotations

from fastapi import APIRouter
from sqlalchemy import text

from app.api.deps import SessionDep
from app.config.settings import get_settings

router = APIRouter(tags=["health"])


@router.get("/")
async def root() -> dict[str, str]:
    """Basic service root endpoint for host health checks."""
    return {"status": "ok", "app": get_settings().app_name}


@router.get("/health")
async def health() -> dict[str, str]:
    """Liveness probe."""
    return {"status": "ok", "app": get_settings().app_name}


@router.get("/health/ready")
async def readiness(session: SessionDep) -> dict[str, str]:
    """Readiness probe — verifies the database is reachable."""
    await session.execute(text("SELECT 1"))
    return {"status": "ready", "app": get_settings().app_name}
