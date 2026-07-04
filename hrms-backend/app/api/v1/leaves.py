from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import crud
from app.core.dependencies import get_current_user, require_admin
from app.database import get_db
from app.models.models import LeaveStatus, User
from app.schemas.schemas import LeaveAction, LeaveApply, LeaveRequestOut

router = APIRouter(prefix="/leaves", tags=["Leave Management"])


@router.post(
    "/apply",
    response_model=LeaveRequestOut,
    status_code=status.HTTP_201_CREATED,
    summary="Apply for leave",
)
async def apply_leave(
    data: LeaveApply,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Submit a leave request.

    - **type**: PAID | SICK | UNPAID
    - **start_date** / **end_date**: Date range (end must be ≥ start)
    - Raises **409** if dates overlap an existing PENDING or APPROVED request.
    """
    return await crud.apply_leave(db, current_user, data)


@router.get(
    "/my-requests",
    response_model=list[LeaveRequestOut],
    summary="Get my leave requests",
)
async def my_leave_requests(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    skip: int = 0,
    limit: int = 100,
):
    """Return the authenticated employee's leave history, newest first."""
    return await crud.get_my_leaves(db, current_user.id, skip=skip, limit=limit)


@router.get(
    "/",
    response_model=list[LeaveRequestOut],
    summary="[Admin] List all leave requests",
    dependencies=[Depends(require_admin)],
)
async def all_leave_requests(
    db: Annotated[AsyncSession, Depends(get_db)],
    status_filter: LeaveStatus | None = None,
    skip: int = 0,
    limit: int = 200,
):
    """
    Admin view of all leave requests.

    Optionally filter by **status_filter**: PENDING | APPROVED | REJECTED.
    """
    return await crud.get_all_leaves(db, status_filter=status_filter, skip=skip, limit=limit)


@router.patch(
    "/{leave_id}/action",
    response_model=LeaveRequestOut,
    summary="[Admin] Approve or reject a leave request",
    dependencies=[Depends(require_admin)],
)
async def action_on_leave(
    leave_id: str,
    data: LeaveAction,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Approve or reject a pending leave request.

    - **action**: APPROVED | REJECTED
    - **admin_comment**: Optional HR comment
    - On **APPROVED**: automatically creates LEAVE attendance records for each day in the range.
    - Raises **409** if the request is already actioned.
    """
    return await crud.action_on_leave(db, leave_id, data)
