"""Tests for employee profile endpoints."""
import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


async def test_get_my_profile(client: AsyncClient, employee_token: str):
    resp = await client.get(
        "/api/v1/employees/me",
        headers={"Authorization": f"Bearer {employee_token}"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["email"] == "employee@test.com"
    assert data["role"] == "EMPLOYEE"


async def test_update_my_profile(client: AsyncClient, employee_token: str):
    resp = await client.put(
        "/api/v1/employees/me",
        headers={"Authorization": f"Bearer {employee_token}"},
        json={"phone": "9876543210", "address": "123 Test Street"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["phone"] == "9876543210"
    assert data["address"] == "123 Test Street"


async def test_employee_cannot_list_all_employees(client: AsyncClient, employee_token: str):
    resp = await client.get(
        "/api/v1/employees/",
        headers={"Authorization": f"Bearer {employee_token}"},
    )
    assert resp.status_code == 403


async def test_admin_can_list_all_employees(client: AsyncClient, admin_token: str):
    resp = await client.get(
        "/api/v1/employees/",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


async def test_admin_can_get_employee_by_id(
    client: AsyncClient, employee_token: str, admin_token: str
):
    # Get employee's own ID first
    me_resp = await client.get(
        "/api/v1/employees/me",
        headers={"Authorization": f"Bearer {employee_token}"},
    )
    emp_id = me_resp.json()["id"]

    resp = await client.get(
        f"/api/v1/employees/{emp_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp.status_code == 200
    assert resp.json()["id"] == emp_id


async def test_admin_update_employee(
    client: AsyncClient, employee_token: str, admin_token: str
):
    me_resp = await client.get(
        "/api/v1/employees/me",
        headers={"Authorization": f"Bearer {employee_token}"},
    )
    emp_id = me_resp.json()["id"]

    resp = await client.put(
        f"/api/v1/employees/{emp_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"is_verified": True},
    )
    assert resp.status_code == 200
    assert resp.json()["is_verified"] is True
