"""
Shared pytest fixtures for the HRMS test suite.

Uses an in-memory SQLite DB (via aiosqlite) — works because the ORM models
use cross-dialect SQLAlchemy types (Uuid, JSON, native_enum=False).
"""
import asyncio
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app

# ─── In-memory test database ──────────────────────────────────────────────────
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
    future=True,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


@pytest_asyncio.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session", autouse=True)
async def create_test_tables():
    """Create all tables once per test session."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Fresh session per test, rolled back after each test."""
    async with TestSessionLocal() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """AsyncClient that overrides the DB dependency with the test session."""

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac

    app.dependency_overrides.clear()


# ─── Helper fixtures ──────────────────────────────────────────────────────────

@pytest_asyncio.fixture
async def employee_token(client: AsyncClient) -> str:
    """Register and log in a test employee, return their access token."""
    await client.post("/api/v1/auth/register", json={
        "employee_id": "EMP-001",
        "email": "employee@test.com",
        "password": "testpass123",
        "full_name": "Test Employee",
        "role": "EMPLOYEE",
    })
    resp = await client.post("/api/v1/auth/login", data={
        "username": "employee@test.com",
        "password": "testpass123",
    })
    return resp.json()["access_token"]


@pytest_asyncio.fixture
async def admin_token(client: AsyncClient) -> str:
    """Register and log in a test admin, return their access token."""
    await client.post("/api/v1/auth/register", json={
        "employee_id": "ADM-001",
        "email": "admin@test.com",
        "password": "adminpass123",
        "full_name": "Test Admin",
        "role": "HR_ADMIN",
    })
    resp = await client.post("/api/v1/auth/login", data={
        "username": "admin@test.com",
        "password": "adminpass123",
    })
    return resp.json()["access_token"]
