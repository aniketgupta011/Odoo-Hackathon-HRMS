"""Tests for leave management workflow."""
import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio

FUTURE_START = "2099-12-01"
FUTURE_END = "2099-12-05"
OVERLAP_START = "2099-12-03"
OVERLAP_END = "2099-12-07"


async def test_apply_leave_success(client: AsyncClient, employee_token: str):
    resp = await client.post(
        "/api/v1/leaves/apply",
        headers={"Authorization": f"Bearer {employee_token}"},
        json={
            "type": "PAID",
            "start_date": FUTURE_START,
            "end_date": FUTURE_END,
            "remarks": "Annual vacation",
        },
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["status"] == "PENDING"
    assert data["type"] == "PAID"


async def test_apply_leave_invalid_dates(client: AsyncClient, employee_token: str):
    resp = await client.post(
        "/api/v1/leaves/apply",
        headers={"Authorization": f"Bearer {employee_token}"},
        json={
            "type": "SICK",
            "start_date": FUTURE_END,   # end before start
            "end_date": FUTURE_START,
        },
    )
    assert resp.status_code == 422


async def test_apply_overlapping_leave(client: AsyncClient, employee_token: str):
    # First request
    await client.post(
        "/api/v1/leaves/apply",
        headers={"Authorization": f"Bearer {employee_token}"},
        json={"type": "PAID", "start_date": FUTURE_START, "end_date": FUTURE_END},
    )
    # Overlapping request
    resp = await client.post(
        "/api/v1/leaves/apply",
        headers={"Authorization": f"Bearer {employee_token}"},
        json={"type": "SICK", "start_date": OVERLAP_START, "end_date": OVERLAP_END},
    )
    assert resp.status_code == 409


async def test_get_my_leave_requests(client: AsyncClient, employee_token: str):
    await client.post(
        "/api/v1/leaves/apply",
        headers={"Authorization": f"Bearer {employee_token}"},
        json={"type": "UNPAID", "start_date": "2099-11-01", "end_date": "2099-11-02"},
    )
    resp = await client.get(
        "/api/v1/leaves/my-requests",
        headers={"Authorization": f"Bearer {employee_token}"},
    )
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)
    assert len(resp.json()) >= 1


async def test_admin_approve_leave(client: AsyncClient, employee_token: str, admin_token: str):
    # Employee applies
    apply_resp = await client.post(
        "/api/v1/leaves/apply",
        headers={"Authorization": f"Bearer {employee_token}"},
        json={"type": "PAID", "start_date": "2099-10-01", "end_date": "2099-10-03"},
    )
    leave_id = apply_resp.json()["id"]

    # Admin approves
    resp = await client.patch(
        f"/api/v1/leaves/{leave_id}/action",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"action": "APPROVED", "admin_comment": "Enjoy your time off!"},
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "APPROVED"
    assert resp.json()["admin_comment"] == "Enjoy your time off!"


async def test_admin_reject_leave(client: AsyncClient, employee_token: str, admin_token: str):
    apply_resp = await client.post(
        "/api/v1/leaves/apply",
        headers={"Authorization": f"Bearer {employee_token}"},
        json={"type": "SICK", "start_date": "2099-09-10", "end_date": "2099-09-10"},
    )
    leave_id = apply_resp.json()["id"]

    resp = await client.patch(
        f"/api/v1/leaves/{leave_id}/action",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"action": "REJECTED", "admin_comment": "Peak period — cannot approve"},
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "REJECTED"


async def test_double_action_blocked(client: AsyncClient, employee_token: str, admin_token: str):
    apply_resp = await client.post(
        "/api/v1/leaves/apply",
        headers={"Authorization": f"Bearer {employee_token}"},
        json={"type": "PAID", "start_date": "2099-08-01", "end_date": "2099-08-01"},
    )
    leave_id = apply_resp.json()["id"]
    # First action
    await client.patch(
        f"/api/v1/leaves/{leave_id}/action",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"action": "APPROVED"},
    )
    # Second action on already-decided leave
    resp = await client.patch(
        f"/api/v1/leaves/{leave_id}/action",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"action": "REJECTED"},
    )
    assert resp.status_code == 409


async def test_employee_cannot_action_leave(
    client: AsyncClient, employee_token: str
):
    apply_resp = await client.post(
        "/api/v1/leaves/apply",
        headers={"Authorization": f"Bearer {employee_token}"},
        json={"type": "PAID", "start_date": "2099-07-01", "end_date": "2099-07-02"},
    )
    leave_id = apply_resp.json()["id"]
    resp = await client.patch(
        f"/api/v1/leaves/{leave_id}/action",
        headers={"Authorization": f"Bearer {employee_token}"},
        json={"action": "APPROVED"},
    )
    assert resp.status_code == 403


async def test_admin_list_all_leaves(client: AsyncClient, admin_token: str):
    resp = await client.get(
        "/api/v1/leaves/",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)
