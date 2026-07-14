"""API tests for authentication and RBAC-guarded user management."""

from __future__ import annotations

from httpx import AsyncClient

from tests.conftest import ADMIN_EMAIL, ADMIN_PASSWORD, VIEWER_EMAIL


async def test_health(client: AsyncClient) -> None:
    resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


async def test_login_success(client: AsyncClient) -> None:
    resp = await client.post(
        "/api/v1/auth/login",
        json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["access_token"] and body["refresh_token"]
    assert body["token_type"] == "bearer"


async def test_login_wrong_password(client: AsyncClient) -> None:
    resp = await client.post(
        "/api/v1/auth/login",
        json={"email": ADMIN_EMAIL, "password": "nope"},
    )
    assert resp.status_code == 401


async def test_me_requires_auth(client: AsyncClient) -> None:
    resp = await client.get("/api/v1/auth/me")
    assert resp.status_code == 401


async def test_me_returns_profile(client: AsyncClient, admin_token: str) -> None:
    resp = await client.get(
        "/api/v1/auth/me", headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["email"] == ADMIN_EMAIL
    assert body["role"] == "admin"


async def test_refresh_flow(client: AsyncClient) -> None:
    login = await client.post(
        "/api/v1/auth/login",
        json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
    )
    refresh_token = login.json()["refresh_token"]
    resp = await client.post(
        "/api/v1/auth/refresh", json={"refresh_token": refresh_token}
    )
    assert resp.status_code == 200
    assert resp.json()["access_token"]


async def test_refresh_rejects_access_token(
    client: AsyncClient, admin_token: str
) -> None:
    resp = await client.post(
        "/api/v1/auth/refresh", json={"refresh_token": admin_token}
    )
    assert resp.status_code == 401


async def test_admin_can_create_user(client: AsyncClient, admin_token: str) -> None:
    resp = await client.post(
        "/api/v1/users",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "email": "newsre@sentinel.ai",
            "full_name": "New SRE",
            "password": "new-sre-password",
            "role": "sre",
        },
    )
    assert resp.status_code == 201, resp.text
    assert resp.json()["role"] == "sre"


async def test_duplicate_user_conflicts(client: AsyncClient, admin_token: str) -> None:
    resp = await client.post(
        "/api/v1/users",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "email": VIEWER_EMAIL,
            "full_name": "Dup",
            "password": "some-password",
            "role": "viewer",
        },
    )
    assert resp.status_code == 409


async def test_viewer_forbidden_from_creating_users(
    client: AsyncClient, viewer_token: str
) -> None:
    resp = await client.post(
        "/api/v1/users",
        headers={"Authorization": f"Bearer {viewer_token}"},
        json={
            "email": "x@sentinel.ai",
            "full_name": "X",
            "password": "password-123",
            "role": "viewer",
        },
    )
    assert resp.status_code == 403


async def test_viewer_forbidden_from_listing_users(
    client: AsyncClient, viewer_token: str
) -> None:
    resp = await client.get(
        "/api/v1/users", headers={"Authorization": f"Bearer {viewer_token}"}
    )
    assert resp.status_code == 403


async def test_admin_can_list_users(client: AsyncClient, admin_token: str) -> None:
    resp = await client.get(
        "/api/v1/users", headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert resp.status_code == 200
    assert len(resp.json()) >= 2
