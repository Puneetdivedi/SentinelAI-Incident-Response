"""Authentication routes: login, refresh, current-user."""

from __future__ import annotations

from fastapi import APIRouter, Request, status

from app.api.deps import AuditServiceDep, AuthServiceDep, CurrentUser
from app.schemas.auth import LoginRequest, RefreshRequest, TokenPair
from app.schemas.user import UserRead

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenPair)
async def login(
    payload: LoginRequest,
    request: Request,
    auth_service: AuthServiceDep,
    audit: AuditServiceDep,
) -> TokenPair:
    """Authenticate with email + password and receive an access/refresh token pair."""
    user, tokens = await auth_service.login(payload.email, payload.password)
    await audit.record(
        action="auth.login",
        resource_type="user",
        actor_id=user.id,
        resource_id=user.id,
        ip_address=request.client.host if request.client else None,
    )
    return tokens


@router.post("/refresh", response_model=TokenPair)
async def refresh(payload: RefreshRequest, auth_service: AuthServiceDep) -> TokenPair:
    """Exchange a valid refresh token for a new token pair."""
    return await auth_service.refresh(payload.refresh_token)


@router.get("/me", response_model=UserRead, status_code=status.HTTP_200_OK)
async def me(current_user: CurrentUser) -> UserRead:
    """Return the currently authenticated user's profile."""
    return UserRead.model_validate(current_user)
