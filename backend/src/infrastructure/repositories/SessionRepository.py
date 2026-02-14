from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlmodel import delete, select

from src.application.interfaces.SessionRepositoryInterface import sessionRepositoryInterface
from src.domain.enums.SessionStatusEnum import sessionStatusEnum
from src.domain.models.SessionModel import sessionModel

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class sessionRepository(sessionRepositoryInterface):

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def find_by_id(self, session_id: str) -> sessionModel | None:
        stmt = select(sessionModel).where(sessionModel.id == session_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_by_user_id(self, user_id: str) -> list[sessionModel]:
        stmt = select(sessionModel).where(sessionModel.user_id == user_id).order_by(sessionModel.created_at.desc())
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def find_active_by_user_id(self, user_id: str) -> list[sessionModel]:
        stmt = (
            select(sessionModel)
            .where(sessionModel.user_id == user_id)
            .where(sessionModel.status == sessionStatusEnum.ACTIVE)
            .order_by(sessionModel.last_activity.desc())
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def count_active_by_user_id(self, user_id: str) -> int:
        from sqlalchemy import func

        stmt = (
            select(func.count())
            .select_from(sessionModel)
            .where(sessionModel.user_id == user_id)
            .where(sessionModel.status == sessionStatusEnum.ACTIVE)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one()

    async def save(self, session: sessionModel) -> sessionModel:
        self._session.add(session)
        await self._session.flush()
        await self._session.refresh(session)
        return session

    async def update(self, session: sessionModel) -> sessionModel:
        self._session.add(session)
        await self._session.flush()
        await self._session.refresh(session)
        return session

    async def delete_expired(self, before: datetime) -> int:
        stmt = delete(sessionModel).where(
            sessionModel.expires_at < before,
            sessionModel.status != sessionStatusEnum.ACTIVE,
        )
        result = await self._session.execute(stmt)
        return result.rowcount
