"""
HRMS FastAPI application entry point.

- Mounts the versioned API routers
- Configures CORS for the Angular frontend
- Auto-creates SQLite tables on startup
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import auth, employees, attendance, leaves, payroll
from app.database import Base, engine

# Import models so they register on Base.metadata before create_all
import app.models.models  # noqa: F401


@asynccontextmanager
async def lifespan(application: FastAPI):
    """Create all tables on startup (SQLite file is auto-created)."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(
    title="HRMS API",
    description="Human Resource Management System — FastAPI Backend",
    version="1.0.0",
    lifespan=lifespan,
)

# ─── CORS ─────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:4200",   # Angular dev server
        "http://127.0.0.1:4200",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── API v1 routers ───────────────────────────────────────────────────────────
API_V1_PREFIX = "/api/v1"

app.include_router(auth.router,       prefix=API_V1_PREFIX)
app.include_router(employees.router,  prefix=API_V1_PREFIX)
app.include_router(attendance.router, prefix=API_V1_PREFIX)
app.include_router(leaves.router,     prefix=API_V1_PREFIX)
app.include_router(payroll.router,    prefix=API_V1_PREFIX)


@app.get("/", tags=["Health"])
def read_root():
    return {"status": "ok", "message": "HRMS API is running"}