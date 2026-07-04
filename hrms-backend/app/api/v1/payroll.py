import uuid
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import crud
from app.core.dependencies import get_current_user, require_admin
from app.database import get_db
from app.models.models import User
from app.schemas.schemas import PayrollOut, PayrollUpdate

router = APIRouter(prefix="/payroll", tags=["Payroll"])


@router.get(
    "/me",
    response_model=PayrollOut,
    summary="Get my salary structure",
)
async def get_my_payroll(
    current_user: Annotated[User, Depends(get_current_user)],
):
    """
    Read-only view of the authenticated employee's salary structure.

    Returns the JSONB salary breakdown stored in the user profile.
    """
    return PayrollOut(
        employee_id=current_user.id,
        salary_structure=current_user.salary_structure,
    )


@router.put(
    "/{employee_id}",
    response_model=PayrollOut,
    summary="[Admin] Update employee salary structure",
    dependencies=[Depends(require_admin)],
)
async def update_payroll(
    employee_id: uuid.UUID,
    data: PayrollUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Replace the salary structure for a given employee. **Admin only.**

    Accepts any valid JSON object. Recommended structure:
    ```json
    {
      "basic": 50000,
      "hra": 20000,
      "allowances": 5000,
      "deductions": 3000,
      "currency": "INR"
    }
    ```
    """
    user = await crud.update_payroll(db, employee_id, data.salary_structure)
    return PayrollOut(employee_id=user.id, salary_structure=user.salary_structure)
