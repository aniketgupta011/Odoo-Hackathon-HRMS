"""Tests for authentication endpoints."""
import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


async def test_register_success(client: AsyncClient):
    resp = await client.post("/api/v1/auth/register", json={
        "employee_id": "EMP-100",
        "email": "newuser@test.com",
        "password": "securepass",
        "full_name": "New User",
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["email"] == "newuser@test.com"
    assert data["employee_id"] == "EMP-100"
    assert data["role"] == "EMPLOYEE"
    assert "hashed_password" not in data


async def test_register_duplicate_email(client: AsyncClient):
    payload = {
        "employee_id": "EMP-200",
        "email": "dup@test.com",
        "password": "securepass",
    }
    await client.post("/api/v1/auth/register", json=payload)
    # Second registration with same email
    payload["employee_id"] = "EMP-201"
    resp = await client.post("/api/v1/auth/register", json=payload)
    assert resp.status_code == 409


async def test_register_duplicate_employee_id(client: AsyncClient):
    payload = {
        "employee_id": "EMP-300",
        "email": "first300@test.com",
        "password": "securepass",
    }
    await client.post("/api/v1/auth/register", json=payload)
    # Same employee_id, different email
    payload["email"] = "second300@test.com"
    resp = await client.post("/api/v1/auth/register", json=payload)
    assert resp.status_code == 409


async def test_login_success(client: AsyncClient):
    await client.post("/api/v1/auth/register", json={
        "employee_id": "EMP-400",
        "email": "login@test.com",
        "password": "mypassword",
    })
    resp = await client.post("/api/v1/auth/login", data={
        "username": "login@test.com",
        "password": "mypassword",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


async def test_login_wrong_password(client: AsyncClient):
    await client.post("/api/v1/auth/register", json={
        "employee_id": "EMP-500",
        "email": "badpass@test.com",
        "password": "correctpass",
    })
    resp = await client.post("/api/v1/auth/login", data={
        "username": "badpass@test.com",
        "password": "wrongpass",
    })
    assert resp.status_code == 401


async def test_login_nonexistent_user(client: AsyncClient):
    resp = await client.post("/api/v1/auth/login", data={
        "username": "ghost@test.com",
        "password": "whatever",
    })
    assert resp.status_code == 401


async def test_protected_route_without_token(client: AsyncClient):
    resp = await client.get("/api/v1/employees/me")
    assert resp.status_code == 401


async def test_protected_route_with_invalid_token(client: AsyncClient):
    resp = await client.get(
        "/api/v1/employees/me",
        headers={"Authorization": "Bearer this.is.fake"},
    )
    assert resp.status_code == 401
