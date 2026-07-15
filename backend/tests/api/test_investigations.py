"""End-to-end API tests for the incident → investigate → approve flow."""

from __future__ import annotations

from httpx import AsyncClient


def _auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


async def _create_incident(client: AsyncClient, token: str) -> str:
    resp = await client.post(
        "/api/v1/incidents",
        headers=_auth(token),
        json={
            "title": "Login failures",
            "description": "Users cannot log in; auth API returns HTTP 500.",
            "severity": "sev1",
            "affected_service": "auth-api",
        },
    )
    assert resp.status_code == 201, resp.text
    return resp.json()["id"]


async def test_create_and_get_incident(client: AsyncClient, admin_token: str) -> None:
    incident_id = await _create_incident(client, admin_token)
    resp = await client.get(f"/api/v1/incidents/{incident_id}", headers=_auth(admin_token))
    assert resp.status_code == 200
    assert resp.json()["status"] == "investigating" or resp.json()["status"] == "open"


async def test_full_investigation_flow_approved(client: AsyncClient, admin_token: str) -> None:
    incident_id = await _create_incident(client, admin_token)

    inv = await client.post(
        f"/api/v1/incidents/{incident_id}/investigate",
        headers=_auth(admin_token),
        json={},
    )
    assert inv.status_code == 201, inv.text
    detail = inv.json()
    assert detail["status"] == "awaiting_approval"
    assert detail["approval_status"] == "pending"
    assert detail["root_cause_candidates"], "root causes should be persisted"
    assert detail["recommendations"], "recommendations should be persisted"
    assert detail["reports"], "a report should be generated"
    assert detail["timeline"] and detail["metrics"] and detail["deployments"]
    top = max(detail["root_cause_candidates"], key=lambda c: c["confidence"])
    assert top["category"] == "bad_deployment"

    investigation_id = detail["id"]

    # Approve remediation.
    approve = await client.post(
        f"/api/v1/investigations/{investigation_id}/approve",
        headers=_auth(admin_token),
        json={"approved": True, "note": "Rollback authorized"},
    )
    assert approve.status_code == 200, approve.text
    assert approve.json()["status"] == "completed"
    assert approve.json()["approval_status"] == "approved"


async def test_investigation_reject(client: AsyncClient, admin_token: str) -> None:
    incident_id = await _create_incident(client, admin_token)
    inv = await client.post(
        f"/api/v1/incidents/{incident_id}/investigate", headers=_auth(admin_token), json={}
    )
    investigation_id = inv.json()["id"]
    resp = await client.post(
        f"/api/v1/investigations/{investigation_id}/approve",
        headers=_auth(admin_token),
        json={"approved": False},
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "rejected"
    assert resp.json()["approval_status"] == "rejected"


async def test_get_and_list_investigations(client: AsyncClient, admin_token: str) -> None:
    incident_id = await _create_incident(client, admin_token)
    inv = await client.post(
        f"/api/v1/incidents/{incident_id}/investigate", headers=_auth(admin_token), json={}
    )
    investigation_id = inv.json()["id"]

    detail = await client.get(
        f"/api/v1/investigations/{investigation_id}", headers=_auth(admin_token)
    )
    assert detail.status_code == 200
    assert detail.json()["id"] == investigation_id

    listing = await client.get(
        "/api/v1/investigations",
        headers=_auth(admin_token),
        params={"incident_id": incident_id},
    )
    assert listing.status_code == 200
    assert any(row["id"] == investigation_id for row in listing.json())

    reports = await client.get(
        f"/api/v1/investigations/{investigation_id}/reports", headers=_auth(admin_token)
    )
    assert reports.status_code == 200 and reports.json()


async def test_double_approve_is_rejected(client: AsyncClient, admin_token: str) -> None:
    incident_id = await _create_incident(client, admin_token)
    inv = await client.post(
        f"/api/v1/incidents/{incident_id}/investigate", headers=_auth(admin_token), json={}
    )
    investigation_id = inv.json()["id"]
    await client.post(
        f"/api/v1/investigations/{investigation_id}/approve",
        headers=_auth(admin_token), json={"approved": True},
    )
    # Second decision must fail (no longer awaiting approval).
    again = await client.post(
        f"/api/v1/investigations/{investigation_id}/approve",
        headers=_auth(admin_token), json={"approved": True},
    )
    assert again.status_code == 422


# ── RBAC ─────────────────────────────────────────────────────
async def test_viewer_cannot_create_incident(client: AsyncClient, viewer_token: str) -> None:
    resp = await client.post(
        "/api/v1/incidents",
        headers=_auth(viewer_token),
        json={"title": "x", "description": "y", "severity": "sev3"},
    )
    assert resp.status_code == 403


async def test_viewer_cannot_investigate(
    client: AsyncClient, admin_token: str, viewer_token: str
) -> None:
    incident_id = await _create_incident(client, admin_token)
    resp = await client.post(
        f"/api/v1/incidents/{incident_id}/investigate",
        headers=_auth(viewer_token), json={},
    )
    assert resp.status_code == 403


async def test_viewer_can_read_incidents(
    client: AsyncClient, admin_token: str, viewer_token: str
) -> None:
    await _create_incident(client, admin_token)
    resp = await client.get("/api/v1/incidents", headers=_auth(viewer_token))
    assert resp.status_code == 200
    assert len(resp.json()) >= 1
