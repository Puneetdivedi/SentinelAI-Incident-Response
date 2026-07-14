"""Aggregate v1 API router.

New feature routers (incidents, investigations, reports) are added here in later phases.
"""

from __future__ import annotations

from fastapi import APIRouter

from app.api.v1.routes import auth, users

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(users.router)
