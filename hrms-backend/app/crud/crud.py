"""
CRUD layer — all database operations.

Each function receives an AsyncSession and returns ORM objects or raises
HTTPException for business-rule violations.
"""
from __future__ import annotations

import uuid
from datetime import date, datetime, timedelta, timezone
from typing import Any, Sequence

from fastapi import HTTPException, status
from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password, verify_password
from app.models.models import (
    Attendance,
    AttendanceStatus,
    LeaveRequest,
    LeaveStatus,
    LeaveType,
    User,
    UserRole,
)
from app.schemas.schemas import (
    LeaveAction,
    LeaveApply,
    UserAdminUpdate,
    UserRegister,
    UserSelfUpdate,
)


# ─── User CRUD ────────────────────────────────────────────────────────────────

async def create_user(db: AsyncSession, data: UserRegister) -> User:
    """Register a new user after checking for duplicate email/employee_id."""
    # Check email uniqueness
    existing_email = await db.execute(select(User).where(User.email == data.email))
    if existing_email.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email already exists",
        )
    # Check employee_id uniqueness
    existing_emp = await db.execute(select(User).where(User.employee_id == data.employee_id))
    if existing_emp.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this employee_id already exists",
        )

    user = User(
        employee_id=data.employee_id,
        email=data.email,
        hashed_password=hash_password(data.password),
        role=data.role,
        full_name=data.full_name,
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)
    return user


async def authenticate_user(db: AsyncSession, email: str, password: str) -> User:
    """Return user if credentials are valid, else raise 401."""
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


async def get_user_by_id(db: AsyncSession, user_id: str | uuid.UUID) -> User:
    try:
        uid = uuid.UUID(str(user_id))
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    result = await db.execute(select(User).where(User.id == uid))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


async def get_all_users(db: AsyncSession, skip: int = 0, limit: int = 100) -> Sequence[User]:
    result = await db.execute(select(User).offset(skip).limit(limit))
    return result.scalars().all()


async def update_user_self(db: AsyncSession, user: User, data: UserSelfUpdate) -> User:
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)
    await db.flush()
    await db.refresh(user)
    return user


async def update_user_admin(
    db: AsyncSession, user_id: str | uuid.UUID, data: UserAdminUpdate
) -> User:
    user = await get_user_by_id(db, user_id)
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)
    await db.flush()
    await db.refresh(user)
    return user


# ─── Attendance CRUD ──────────────────────────────────────────────────────────

async def check_in(db: AsyncSession, employee: User) -> Attendance:
    today = datetime.now(timezone.utc).date()

    # Block double check-in
    existing = await db.execute(
        select(Attendance).where(
            and_(Attendance.employee_id == employee.id, Attendance.date == today)
        )
    )
    record = existing.scalar_one_or_none()

    if record:
        if record.check_in is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="You have already checked in today",
            )
        # Rare: record exists but no check_in (e.g., manually created ABSENT)
        record.check_in = datetime.now(timezone.utc)
        record.status = AttendanceStatus.PRESENT
    else:
        record = Attendance(
            employee_id=employee.id,
            date=today,
            check_in=datetime.now(timezone.utc),
            status=AttendanceStatus.PRESENT,
        )
        db.add(record)

    await db.flush()
    await db.refresh(record)
    return record


async def check_out(db: AsyncSession, employee: User) -> Attendance:
    today = datetime.now(timezone.utc).date()

    existing = await db.execute(
        select(Attendance).where(
            and_(Attendance.employee_id == employee.id, Attendance.date == today)
        )
    )
    record = existing.scalar_one_or_none()

    if not record or record.check_in is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have not checked in today",
        )
    if record.check_out is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="You have already checked out today",
        )

    record.check_out = datetime.now(timezone.utc)

    # Determine HALF_DAY if total hours < 4
    # Normalize to UTC-naive for SQLite compatibility (SQLite stores naive datetimes)
    checkout_utc = record.check_out.replace(tzinfo=None)
    checkin_raw = record.check_in
    if hasattr(checkin_raw, 'tzinfo') and checkin_raw.tzinfo is not None:
        checkin_utc = checkin_raw.replace(tzinfo=None)
    else:
        checkin_utc = checkin_raw
    duration = checkout_utc - checkin_utc
    if duration.total_seconds() < 4 * 3600:
        record.status = AttendanceStatus.HALF_DAY

    await db.flush()
    await db.refresh(record)
    return record


async def get_my_attendance(
    db: AsyncSession,
    employee_id: uuid.UUID,
    start_date: date | None = None,
    end_date: date | None = None,
    skip: int = 0,
    limit: int = 100,
) -> Sequence[Attendance]:
    query = select(Attendance).where(Attendance.employee_id == employee_id)
    if start_date:
        query = query.where(Attendance.date >= start_date)
    if end_date:
        query = query.where(Attendance.date <= end_date)
    query = query.order_by(Attendance.date.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


async def get_all_attendance(
    db: AsyncSession,
    employee_id: uuid.UUID | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
    skip: int = 0,
    limit: int = 200,
) -> Sequence[Attendance]:
    query = select(Attendance)
    if employee_id:
        query = query.where(Attendance.employee_id == employee_id)
    if start_date:
        query = query.where(Attendance.date >= start_date)
    if end_date:
        query = query.where(Attendance.date <= end_date)
    query = query.order_by(Attendance.date.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


# ─── Leave CRUD ───────────────────────────────────────────────────────────────

async def apply_leave(db: AsyncSession, employee: User, data: LeaveApply) -> LeaveRequest:
    """Apply for leave with date-range validation and overlap detection."""
    if data.end_date < data.start_date:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="end_date must be on or after start_date",
        )

    # Check for overlapping leave requests (PENDING or APPROVED)
    overlap_check = await db.execute(
        select(LeaveRequest).where(
            and_(
                LeaveRequest.employee_id == employee.id,
                LeaveRequest.status.in_([LeaveStatus.PENDING, LeaveStatus.APPROVED]),
                LeaveRequest.start_date <= data.end_date,
                LeaveRequest.end_date >= data.start_date,
            )
        )
    )
    if overlap_check.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="You already have an overlapping leave request for this date range",
        )

    leave = LeaveRequest(
        employee_id=employee.id,
        type=data.type,
        start_date=data.start_date,
        end_date=data.end_date,
        remarks=data.remarks,
        status=LeaveStatus.PENDING,
    )
    db.add(leave)
    await db.flush()
    await db.refresh(leave)
    return leave


async def get_my_leaves(
    db: AsyncSession, employee_id: uuid.UUID, skip: int = 0, limit: int = 100
) -> Sequence[LeaveRequest]:
    result = await db.execute(
        select(LeaveRequest)
        .where(LeaveRequest.employee_id == employee_id)
        .order_by(LeaveRequest.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()


async def get_all_leaves(
    db: AsyncSession,
    status_filter: LeaveStatus | None = None,
    skip: int = 0,
    limit: int = 200,
) -> Sequence[LeaveRequest]:
    query = select(LeaveRequest)
    if status_filter:
        query = query.where(LeaveRequest.status == status_filter)
    query = query.order_by(LeaveRequest.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


async def action_on_leave(
    db: AsyncSession, leave_id: str, data: LeaveAction
) -> LeaveRequest:
    """Admin approves or rejects a leave request. On approval, creates attendance LEAVE records."""
    result = await db.execute(select(LeaveRequest).where(LeaveRequest.id == leave_id))
    leave = result.scalar_one_or_none()
    if not leave:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Leave request not found")
    if leave.status != LeaveStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Leave request is already {leave.status}",
        )

    leave.status = data.action
    leave.admin_comment = data.admin_comment

    # On approval → auto-create LEAVE attendance records for each calendar day
    if data.action == LeaveStatus.APPROVED:
        delta = leave.end_date - leave.start_date
        for i in range(delta.days + 1):
            leave_date = leave.start_date + timedelta(days=i)
            # Only create if no record exists for that day
            existing = await db.execute(
                select(Attendance).where(
                    and_(
                        Attendance.employee_id == leave.employee_id,
                        Attendance.date == leave_date,
                    )
                )
            )
            if not existing.scalar_one_or_none():
                attendance_record = Attendance(
                    employee_id=leave.employee_id,
                    date=leave_date,
                    status=AttendanceStatus.LEAVE,
                )
                db.add(attendance_record)

    await db.flush()
    await db.refresh(leave)
    return leave


# ─── Payroll CRUD ─────────────────────────────────────────────────────────────

async def get_payroll(db: AsyncSession, user_id: str | uuid.UUID) -> User:
    return await get_user_by_id(db, user_id)


async def update_payroll(
    db: AsyncSession, employee_id: str | uuid.UUID, salary_structure: dict[str, Any]
) -> User:
    user = await get_user_by_id(db, employee_id)
    user.salary_structure = salary_structure
    await db.flush()
    await db.refresh(user)
    return user
