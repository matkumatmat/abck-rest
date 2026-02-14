from __future__ import annotations

from typing import TYPE_CHECKING

from sqlmodel import select

from src.application.interfaces.UserRepositoryInterface import userRepositoryInterface
from src.domain.models.UserModel import userModel

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class userRepository(userRepositoryInterface):

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def find_by_id(self, user_id: str) -> userModel | None:
        stmt = select(userModel).where(userModel.id == user_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_by_email(self, email: str) -> userModel | None:
        stmt = select(userModel).where(userModel.email == email)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def save(self, user: userModel) -> userModel:
        self._session.add(user)
        await self._session.flush()
        await self._session.refresh(user)
        return user

    async def update(self, user: userModel) -> userModel:
        self._session.add(user)
        await self._session.flush()
        await self._session.refresh(user)
        return user

    async def email_exists(self, email: str) -> bool:
        stmt = select(userModel.id).where(userModel.email == email).limit(1)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none() is not None
