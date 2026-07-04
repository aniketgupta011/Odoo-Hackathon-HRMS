import uuid
from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import crud
from app.core.dependencies import get_current_user, require_admin
from app.database import get_db
from app.models.models import User
from app.schemas.schemas import AttendanceOut

router = APIRouter(prefix="/attendance", tags=["Attendance"])


@router.post(
    "/check-in",
    response_model=AttendanceOut,
    status_code=status.HTTP_201_CREATED,
    summary="Check in for today",
)
async def check_in(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Record a check-in timestamp for the current date.

    - Raises **409** if you have already checked in today.
    """
    return await crud.check_in(db, current_user)


@router.post(
    "/check-out",
    response_model=AttendanceOut,
    summary="Check out for today",
)
async def check_out(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Record a check-out timestamp for today.

    - Raises **400** if you have not checked in yet today.
    - Raises **409** if you have already checked out.
    - Automatically marks status as **HALF_DAY** if session < 4 hours.
    """
    return await crud.check_out(db, current_user)


@router.get(
    "/my-history",
    response_model=list[AttendanceOut],
    summary="Get my attendance history",
)
async def my_attendance_history(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    start_date: date | None = None,
    end_date: date | None = None,
    skip: int = 0,
    limit: int = 100,
):
    """
    Returns the authenticated employee's attendance records.

    Filter by optional **start_date** and **end_date** query parameters.
    """
    return await crud.get_my_attendance(
        db, current_user.id, start_date=start_date, end_date=end_date, skip=skip, limit=limit
    )


@router.get(
    "/",
    response_model=list[AttendanceOut],
    summary="[Admin] Query all attendance records",
    dependencies=[Depends(require_admin)],
)
async def all_attendance(
    db: Annotated[AsyncSession, Depends(get_db)],
    employee_id: uuid.UUID | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
    skip: int = 0,
    limit: int = 200,
):
    """
    Admin endpoint to retrieve all attendance records with optional filters.

    Filter by **employee_id**, **start_date**, **end_date**.
    """
    return await crud.get_all_attendance(
        db,
        employee_id=employee_id,
        start_date=start_date,
        end_date=end_date,
        skip=skip,
        limit=limit,
    )
