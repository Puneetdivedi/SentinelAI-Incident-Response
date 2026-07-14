"""User-management routes (admin/SRE scoped)."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query, Request, status

from app.api.deps import (
    AuditServiceDep,
    CurrentUser,
    UserServiceDep,
    require_admin,
    require_sre,
)
from app.domain.entities import User
from app.schemas.user import UserCreate, UserRead, UserRoleUpdate, UserUpdate

router = APIRouter(prefix="/users", tags=["users"])


@router.post(
    "",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_admin)],
)
async def create_user(
    payload: UserCreate,
    request: Request,
    users: UserServiceDep,
    audit: AuditServiceDep,
    admin: CurrentUser,
) -> UserRead:
    user = await users.create_user(
        email=payload.email,
        full_name=payload.full_name,
        password=payload.password,
        role=payload.role,
    )
    await audit.record(
        action="user.create",
        resource_type="user",
        actor_id=admin.id,
        resource_id=user.id,
        detail=f"role={payload.role.value}",
        ip_address=request.client.host if request.client else None,
    )
    return UserRead.model_validate(user)


@router.get("", response_model=list[UserRead], dependencies=[Depends(require_sre)])
async def list_users(
    users: UserServiceDep,
    limit: Annotated[int, Query(ge=1, le=200)] = 100,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> list[UserRead]:
    result = await users.list_users(limit=limit, offset=offset)
    return [UserRead.model_validate(u) for u in result]


@router.get(
    "/{user_id}", response_model=UserRead, dependencies=[Depends(require_sre)]
)
async def get_user(user_id: str, users: UserServiceDep) -> UserRead:
    user = await users.get_user(user_id)
    return UserRead.model_validate(user)


@router.patch("/me", response_model=UserRead)
async def update_me(
    payload: UserUpdate, users: UserServiceDep, current_user: CurrentUser
) -> UserRead:
    """Any authenticated user may update their own name/password."""
    updated = await users.update_profile(
        current_user.id, full_name=payload.full_name, password=payload.password
    )
    return UserRead.model_validate(updated)


@router.patch(
    "/{user_id}/role",
    response_model=UserRead,
    dependencies=[Depends(require_admin)],
)
async def change_role(
    user_id: str,
    payload: UserRoleUpdate,
    request: Request,
    users: UserServiceDep,
    audit: AuditServiceDep,
    admin: CurrentUser,
) -> UserRead:
    updated = await users.change_role(user_id, payload.role)
    await audit.record(
        action="user.role_change",
        resource_type="user",
        actor_id=admin.id,
        resource_id=user_id,
        detail=f"role={payload.role.value}",
        ip_address=request.client.host if request.client else None,
    )
    return UserRead.model_validate(updated)


@router.patch(
    "/{user_id}/deactivate",
    response_model=UserRead,
    dependencies=[Depends(require_admin)],
)
async def deactivate_user(
    user_id: str,
    request: Request,
    users: UserServiceDep,
    audit: AuditServiceDep,
    admin: CurrentUser,
) -> UserRead:
    updated = await users.set_active(user_id, is_active=False)
    await audit.record(
        action="user.deactivate",
        resource_type="user",
        actor_id=admin.id,
        resource_id=user_id,
        ip_address=request.client.host if request.client else None,
    )
    return UserRead.model_validate(updated)
