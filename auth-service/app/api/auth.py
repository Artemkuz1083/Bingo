from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user_id
from app.db.session import get_db_session
from app.schemas.auth import AuthResponse, UserLoginRequest, UserRegisterRequest, UserResponse
from app.services.auth import get_current_user, login_user, register_user


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=AuthResponse)
async def register(
    payload: UserRegisterRequest,
    session: AsyncSession = Depends(get_db_session),
) -> AuthResponse:
    return await register_user(session, payload)


@router.post("/login", response_model=AuthResponse)
async def login(
    payload: UserLoginRequest,
    session: AsyncSession = Depends(get_db_session),
) -> AuthResponse:
    return await login_user(session, payload)


@router.get("/me", response_model=UserResponse)
async def me(
    current_user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_db_session),
) -> UserResponse:
    return await get_current_user(session, current_user_id)
