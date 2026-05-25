from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schemas.user import UserUpdateRequest


async def get_user_by_id(session: AsyncSession, user_id: int) -> User:
    user = await session.get(User, user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден.",
        )

    return user


async def update_user_profile(
    session: AsyncSession,
    user_id: int,
    payload: UserUpdateRequest,
) -> User:
    user = await get_user_by_id(session, user_id)

    if payload.username is not None or payload.email is not None:
        duplicate_user = await session.scalar(
            select(User).where(
                User.id != user_id,
                or_(
                    User.username == payload.username,
                    User.email == payload.email,
                ),
            ),
        )

        if duplicate_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Пользователь с таким email или username уже существует.",
            )

    if payload.username is not None:
        user.username = payload.username

    if payload.email is not None:
        user.email = str(payload.email)

    await session.commit()
    await session.refresh(user)
    return user


async def increase_user_balance(
    session: AsyncSession,
    user_id: int,
    amount: Decimal,
) -> User:
    user = await get_user_by_id(session, user_id)
    user.balance += amount

    await session.commit()
    await session.refresh(user)
    return user
