from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schemas.user import UserCreateFromAuthEvent, UserUpdateRequest


async def get_user_by_id(session: AsyncSession, user_id: int) -> User:
    user = await session.get(User, user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Профиль пользователя не найден.",
        )

    return user


async def get_user_by_auth_user_id(session: AsyncSession, auth_user_id: int) -> User:
    user = await session.scalar(select(User).where(User.auth_user_id == auth_user_id))

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Профиль пользователя не найден.",
        )

    return user


async def create_user_from_auth_event(
    session: AsyncSession,
    payload: UserCreateFromAuthEvent,
) -> User:
    existing_user = await session.scalar(
        select(User).where(
            or_(
                User.auth_user_id == payload.auth_user_id,
                User.username == payload.username,
                User.email == payload.email,
            ),
        ),
    )

    if existing_user:
        return existing_user

    user = User(
        auth_user_id=payload.auth_user_id,
        username=payload.username,
        email=str(payload.email),
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


async def update_user_profile(
    session: AsyncSession,
    auth_user_id: int,
    payload: UserUpdateRequest,
) -> User:
    user = await get_user_by_auth_user_id(session, auth_user_id)

    if payload.username is not None or payload.email is not None:
        duplicate_user = await session.scalar(
            select(User).where(
                User.id != user.id,
                or_(
                    User.username == payload.username,
                    User.email == payload.email,
                ),
            ),
        )

        if duplicate_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Профиль с таким email или username уже существует.",
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
    auth_user_id: int,
    amount: Decimal,
) -> User:
    user = await get_user_by_auth_user_id(session, auth_user_id)
    user.balance += amount

    await session.commit()
    await session.refresh(user)
    return user
