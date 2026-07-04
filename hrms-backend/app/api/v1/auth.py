from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import crud
from app.core.config import settings
from app.core.security import create_access_token
from app.database import get_db
from app.schemas.schemas import Token, UserOut, UserRegister

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
)
async def register(
    data: UserRegister,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Create a new HRMS user account.

    - **employee_id**: Unique company ID (e.g. EMP-001)
    - **email**: Unique email address
    - **password**: Minimum 8 characters
    - **role**: EMPLOYEE (default) or HR_ADMIN
    """
    user = await crud.create_user(db, data)
    return user


@router.post(
    "/login",
    response_model=Token,
    summary="Login and receive a JWT access token",
)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    OAuth2-compatible login endpoint.

    - **username**: Your registered email address
    - **password**: Your account password

    Returns a Bearer JWT token. Use it in the `Authorization: Bearer <token>` header.
    """
    user = await crud.authenticate_user(db, form_data.username, form_data.password)
    token_data = {"sub": str(user.id), "role": user.role.value, "email": user.email, "emp": user.employee_id}
    access_token = create_access_token(
        data=token_data,
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return Token(access_token=access_token)
