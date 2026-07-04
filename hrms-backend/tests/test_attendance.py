"""Tests for attendance check-in/check-out endpoints."""
import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


async def test_check_in_success(client: AsyncClient, employee_token: str):
    resp = await client.post(
        "/api/v1/attendance/check-in",
        headers={"Authorization": f"Bearer {employee_token}"},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["check_in"] is not None
    assert data["status"] == "PRESENT"


async def test_double_check_in_blocked(client: AsyncClient, employee_token: str):
    # First check-in
    await client.post(
        "/api/v1/attendance/check-in",
        headers={"Authorization": f"Bearer {employee_token}"},
    )
    # Second check-in same day
    resp = await client.post(
        "/api/v1/attendance/check-in",
        headers={"Authorization": f"Bearer {employee_token}"},
    )
    assert resp.status_code == 409
    assert "already checked in" in resp.json()["detail"]


async def test_check_out_without_check_in(client: AsyncClient, employee_token: str):
    resp = await client.post(
        "/api/v1/attendance/check-out",
        headers={"Authorization": f"Bearer {employee_token}"},
    )
    assert resp.status_code == 400


async def test_check_in_then_check_out(client: AsyncClient, employee_token: str):
    await client.post(
        "/api/v1/attendance/check-in",
        headers={"Authorization": f"Bearer {employee_token}"},
    )
    resp = await client.post(
        "/api/v1/attendance/check-out",
        headers={"Authorization": f"Bearer {employee_token}"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["check_out"] is not None


async def test_double_check_out_blocked(client: AsyncClient, employee_token: str):
    await client.post(
        "/api/v1/attendance/check-in",
        headers={"Authorization": f"Bearer {employee_token}"},
    )
    await client.post(
        "/api/v1/attendance/check-out",
        headers={"Authorization": f"Bearer {employee_token}"},
    )
    resp = await client.post(
        "/api/v1/attendance/check-out",
        headers={"Authorization": f"Bearer {employee_token}"},
    )
    assert resp.status_code == 409


async def test_my_attendance_history(client: AsyncClient, employee_token: str):
    await client.post(
        "/api/v1/attendance/check-in",
        headers={"Authorization": f"Bearer {employee_token}"},
    )
    resp = await client.get(
        "/api/v1/attendance/my-history",
        headers={"Authorization": f"Bearer {employee_token}"},
    )
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)
    assert len(resp.json()) >= 1


async def test_admin_attendance_overview(client: AsyncClient, admin_token: str):
    resp = await client.get(
        "/api/v1/attendance/",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


async def test_employee_cannot_access_admin_attendance(client: AsyncClient, employee_token: str):
    resp = await client.get(
        "/api/v1/attendance/",
        headers={"Authorization": f"Bearer {employee_token}"},
    )
    assert resp.status_code == 403
