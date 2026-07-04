import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import crud
from app.core.dependencies import get_current_user, require_admin
from app.database import get_db
from app.models.models import User
from app.schemas.schemas import UserAdminUpdate, UserOut, UserSelfUpdate

router = APIRouter(prefix="/employees", tags=["Employees"])


@router.get(
    "/me",
    response_model=UserOut,
    summary="Get my profile",
)
async def get_my_profile(
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Return the authenticated user's own profile."""
    return current_user


@router.put(
    "/me",
    response_model=UserOut,
    summary="Update my profile",
)
async def update_my_profile(
    data: UserSelfUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Update self-editable profile fields.

    Employees can only update: **phone**, **address**, **profile_picture_url**, **full_name**.
    """
    return await crud.update_user_self(db, current_user, data)


# ─── Admin-only routes ────────────────────────────────────────────────────────

@router.get(
    "/",
    response_model=list[UserOut],
    summary="[Admin] List all employees",
    dependencies=[Depends(require_admin)],
)
async def list_employees(
    db: Annotated[AsyncSession, Depends(get_db)],
    skip: int = 0,
    limit: int = 100,
):
    """Return a paginated list of all registered employees. **Admin only.**"""
    return await crud.get_all_users(db, skip=skip, limit=limit)


@router.get(
    "/{employee_id}",
    response_model=UserOut,
    summary="[Admin] Get employee by ID",
    dependencies=[Depends(require_admin)],
)
async def get_employee(
    employee_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Fetch a single employee's full profile by UUID. **Admin only.**"""
    return await crud.get_user_by_id(db, employee_id)


@router.put(
    "/{employee_id}",
    response_model=UserOut,
    summary="[Admin] Update any employee's profile",
    dependencies=[Depends(require_admin)],
)
async def update_employee(
    employee_id: uuid.UUID,
    data: UserAdminUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Full profile update including role, email, and verification status.
    **Admin only.**
    """
    return await crud.update_user_admin(db, employee_id, data)
