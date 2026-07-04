import enum
import uuid
from datetime import date, datetime

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    JSON,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.types import Uuid

from app.database import Base


# ─── Enums ────────────────────────────────────────────────────────────────────

class UserRole(str, enum.Enum):
    EMPLOYEE = "EMPLOYEE"
    HR_ADMIN = "HR_ADMIN"


class LeaveStatus(str, enum.Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class LeaveType(str, enum.Enum):
    PAID = "PAID"
    SICK = "SICK"
    UNPAID = "UNPAID"


class AttendanceStatus(str, enum.Enum):
    PRESENT = "PRESENT"
    ABSENT = "ABSENT"
    HALF_DAY = "HALF_DAY"
    LEAVE = "LEAVE"


# ─── User ─────────────────────────────────────────────────────────────────────

class User(Base):
    __tablename__ = "users"

    # Uuid() uses gen_random_uuid() on PostgreSQL and VARCHAR(32) on SQLite
    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    employee_id = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(
        Enum(UserRole, name="user_role", native_enum=False),
        nullable=False,
        default=UserRole.EMPLOYEE,
    )
    full_name = Column(String(100), nullable=True)
    phone = Column(String(20), nullable=True)
    address = Column(Text, nullable=True)
    profile_picture_url = Column(Text, nullable=True)
    # JSON works on both PostgreSQL (stored as JSONB via config) and SQLite
    salary_structure = Column(JSON, nullable=True)
    is_verified = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    attendance_records = relationship(
        "Attendance", back_populates="employee", cascade="all, delete-orphan"
    )
    leave_requests = relationship(
        "LeaveRequest", back_populates="employee", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<User {self.employee_id} ({self.role})>"


# ─── Attendance ───────────────────────────────────────────────────────────────

class Attendance(Base):
    __tablename__ = "attendance"
    __table_args__ = (
        UniqueConstraint("employee_id", "date", name="uq_attendance_employee_date"),
    )

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    employee_id = Column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    date = Column(Date, nullable=False)
    check_in = Column(DateTime(timezone=True), nullable=True)
    check_out = Column(DateTime(timezone=True), nullable=True)
    status = Column(
        Enum(AttendanceStatus, name="attendance_status", native_enum=False),
        nullable=False,
        default=AttendanceStatus.PRESENT,
    )

    # Relationships
    employee = relationship("User", back_populates="attendance_records")

    def __repr__(self) -> str:
        return f"<Attendance employee={self.employee_id} date={self.date} status={self.status}>"


# ─── Leave Request ────────────────────────────────────────────────────────────

class LeaveRequest(Base):
    __tablename__ = "leave_requests"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    employee_id = Column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    type = Column(Enum(LeaveType, name="leave_type", native_enum=False), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    remarks = Column(Text, nullable=True)
    status = Column(
        Enum(LeaveStatus, name="leave_status", native_enum=False),
        nullable=False,
        default=LeaveStatus.PENDING,
    )
    admin_comment = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    employee = relationship("User", back_populates="leave_requests")

    def __repr__(self) -> str:
        return f"<LeaveRequest employee={self.employee_id} {self.start_date}–{self.end_date} ({self.status})>"
