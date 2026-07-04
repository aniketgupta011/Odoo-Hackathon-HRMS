from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.models.models import AttendanceStatus, LeaveStatus, LeaveType, UserRole


# ─── Token Schemas ────────────────────────────────────────────────────────────

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    sub: str | None = None
    role: str | None = None


# ─── User / Auth Schemas ──────────────────────────────────────────────────────

class UserRegister(BaseModel):
    employee_id: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: str | None = Field(None, max_length=100)
    role: UserRole = UserRole.EMPLOYEE


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: uuid.UUID
    employee_id: str
    email: str
    role: UserRole
    full_name: str | None
    phone: str | None
    address: str | None
    profile_picture_url: str | None
    is_verified: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class UserSelfUpdate(BaseModel):
    """Fields an employee can update themselves."""
    phone: str | None = Field(None, max_length=20)
    address: str | None = None
    profile_picture_url: str | None = None
    full_name: str | None = Field(None, max_length=100)


class UserAdminUpdate(UserSelfUpdate):
    """Additional fields only HR_ADMIN can modify."""
    email: EmailStr | None = None
    role: UserRole | None = None
    is_verified: bool | None = None


# ─── Attendance Schemas ───────────────────────────────────────────────────────

class AttendanceOut(BaseModel):
    id: str
    employee_id: uuid.UUID
    date: date
    check_in: datetime | None
    check_out: datetime | None
    status: AttendanceStatus

    model_config = {"from_attributes": True}


# ─── Leave Request Schemas ────────────────────────────────────────────────────

class LeaveApply(BaseModel):
    type: LeaveType
    start_date: date
    end_date: date
    remarks: str | None = None

    @field_validator("end_date")
    @classmethod
    def end_must_be_after_start(cls, end: date, info) -> date:
        start = info.data.get("start_date")
        if start and end < start:
            raise ValueError("end_date must be on or after start_date")
        return end


class LeaveAction(BaseModel):
    action: LeaveStatus = Field(..., description="APPROVED or REJECTED")
    admin_comment: str | None = None

    @field_validator("action")
    @classmethod
    def action_must_be_terminal(cls, v: LeaveStatus) -> LeaveStatus:
        if v == LeaveStatus.PENDING:
            raise ValueError("action must be APPROVED or REJECTED, not PENDING")
        return v


class LeaveRequestOut(BaseModel):
    id: str
    employee_id: uuid.UUID
    type: LeaveType
    start_date: date
    end_date: date
    remarks: str | None
    status: LeaveStatus
    admin_comment: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ─── Payroll Schemas ──────────────────────────────────────────────────────────

class SalaryStructure(BaseModel):
    basic: float = Field(..., ge=0)
    hra: float = Field(0.0, ge=0)
    allowances: float = Field(0.0, ge=0)
    deductions: float = Field(0.0, ge=0)
    currency: str = "INR"

    @property
    def net_salary(self) -> float:
        return self.basic + self.hra + self.allowances - self.deductions


class PayrollUpdate(BaseModel):
    salary_structure: dict[str, Any]


class PayrollOut(BaseModel):
    employee_id: uuid.UUID
    salary_structure: dict[str, Any] | None

    model_config = {"from_attributes": True}
