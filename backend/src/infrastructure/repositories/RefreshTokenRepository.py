from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlmodel import delete, select, update

from src.application.interfaces.RefreshTokenRepositoryInterface import refreshTokenRepositoryInterface
from src.domain.models.RefreshTokenModel import refreshTokenModel

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class refreshTokenRepository(refreshTokenRepositoryInterface):

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def find_by_hash(self, token_hash: str) -> refreshTokenModel | None:
        stmt = select(refreshTokenModel).where(refreshTokenModel.token_hash == token_hash)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_by_session_id(self, session_id: str) -> list[refreshTokenModel]:
        stmt = select(refreshTokenModel).where(refreshTokenModel.session_id == session_id)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def find_active_by_user_id(self, user_id: str) -> list[refreshTokenModel]:
        stmt = (
            select(refreshTokenModel)
            .where(refreshTokenModel.user_id == user_id)
            .where(refreshTokenModel.revoked == False)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def save(self, token: refreshTokenModel) -> refreshTokenModel:
        self._session.add(token)
        await self._session.flush()
        await self._session.refresh(token)
        return token

    async def revoke_by_session(self, session_id: str) -> int:
        stmt = (
            update(refreshTokenModel)
            .where(refreshTokenModel.session_id == session_id)
            .where(refreshTokenModel.revoked == False)
            .values(revoked=True)
        )
        result = await self._session.execute(stmt)
        return result.rowcount

    async def revoke_by_user(self, user_id: str) -> int:
        stmt = (
            update(refreshTokenModel)
            .where(refreshTokenModel.user_id == user_id)
            .where(refreshTokenModel.revoked == False)
            .values(revoked=True)
        )
        result = await self._session.execute(stmt)
        return result.rowcount

    async def delete_expired(self, before: datetime) -> int:
        stmt = delete(refreshTokenModel).where(refreshTokenModel.expires_at < before)
        result = await self._session.execute(stmt)
        return result.rowcount
