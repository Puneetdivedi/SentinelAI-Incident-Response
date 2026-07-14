"""FastAPI dependency providers and RBAC guards.

Wires the request-scoped session into repositories and services (composition at the edge),
and exposes ``get_current_user`` plus a ``require_roles`` guard factory. Routes depend on
these and never construct collaborators themselves.
"""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.settings import Settings, get_settings
from app.database.session import get_session
from app.domain.entities import User
from app.domain.enums import UserRole
from app.domain.exceptions import AuthenticationError
from app.repositories.audit_repository import SqlAlchemyAuditLogRepository
from app.repositories.interfaces import AuditLogRepository, UserRepository
from app.repositories.user_repository import SqlAlchemyUserRepository
from app.services.audit_service import AuditService
from app.services.auth_service import AuthService
from app.services.user_service import UserService
from app.utils.security import decode_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login", auto_error=False)

SettingsDep = Annotated[Settings, Depends(get_settings)]
SessionDep = Annotated[AsyncSession, Depends(get_session)]


# ── Repositories ─────────────────────────────────────────────
def get_user_repository(session: SessionDep) -> UserRepository:
    return SqlAlchemyUserRepository(session)


def get_audit_repository(session: SessionDep) -> AuditLogRepository:
    return SqlAlchemyAuditLogRepository(session)


UserRepoDep = Annotated[UserRepository, Depends(get_user_repository)]
AuditRepoDep = Annotated[AuditLogRepository, Depends(get_audit_repository)]


# ── Services ─────────────────────────────────────────────────
def get_auth_service(settings: SettingsDep, users: UserRepoDep) -> AuthService:
    return AuthService(settings, users)


def get_user_service(users: UserRepoDep) -> UserService:
    return UserService(users)


def get_audit_service(audit: AuditRepoDep) -> AuditService:
    return AuditService(audit)


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]
UserServiceDep = Annotated[UserService, Depends(get_user_service)]
AuditServiceDep = Annotated[AuditService, Depends(get_audit_service)]


# ── Authentication / RBAC ────────────────────────────────────
async def get_current_user(
    settings: SettingsDep,
    users: UserRepoDep,
    token: Annotated[str | None, Depends(oauth2_scheme)],
) -> User:
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        claims = decode_token(settings, token, expected_type="access")
    except AuthenticationError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=exc.message,
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    user = await users.get_by_id(claims.subject)
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is invalid or disabled.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def require_roles(*allowed: UserRole):
    """Return a dependency that enforces the current user holds one of ``allowed``."""

    async def _guard(current_user: CurrentUser) -> User:
        if not current_user.has_role(*allowed):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to perform this action.",
            )
        return current_user

    return _guard


# Convenience role guards.
require_admin = require_roles(UserRole.ADMIN)
require_sre = require_roles(UserRole.ADMIN, UserRole.SRE)
