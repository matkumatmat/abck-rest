from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlmodel import delete, select, update

from src.application.interfaces.PasswordResetRepositoryInterface import passwordResetRepositoryInterface
from src.domain.models.PasswordResetModel import passwordResetModel

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class passwordResetRepository(passwordResetRepositoryInterface):

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def find_by_hash(self, token_hash: str) -> passwordResetModel | None:
        stmt = select(passwordResetModel).where(passwordResetModel.token_hash == token_hash)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_valid_by_user(self, user_id: str) -> passwordResetModel | None:
        now = datetime.now(timezone.utc)
        stmt = (
            select(passwordResetModel)
            .where(passwordResetModel.user_id == user_id)
            .where(passwordResetModel.used == False)
            .where(passwordResetModel.expires_at > now)
            .order_by(passwordResetModel.created_at.desc())
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def save(self, reset: passwordResetModel) -> passwordResetModel:
        self._session.add(reset)
        await self._session.flush()
        await self._session.refresh(reset)
        return reset

    async def update(self, reset: passwordResetModel) -> passwordResetModel:
        self._session.add(reset)
        await self._session.flush()
        await self._session.refresh(reset)
        return reset

    async def delete_expired(self, before: datetime) -> int:
        stmt = delete(passwordResetModel).where(passwordResetModel.expires_at < before)
        result = await self._session.execute(stmt)
        return result.rowcount

    async def invalidate_previous(self, user_id: str) -> int:
        stmt = (
            update(passwordResetModel)
            .where(passwordResetModel.user_id == user_id)
            .where(passwordResetModel.used == False)
            .values(used=True)
        )
        result = await self._session.execute(stmt)
        return result.rowcount
