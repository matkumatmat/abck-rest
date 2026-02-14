from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlmodel import delete, select, update

from src.application.interfaces.VerificationRepositoryInterface import verificationRepositoryInterface
from src.domain.enums.VerificationTypeEnum import verificationTypeEnum
from src.domain.models.VerificationModel import verificationModel

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class verificationRepository(verificationRepositoryInterface):

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def find_by_user_and_type(
        self,
        user_id: str,
        verification_type: verificationTypeEnum,
    ) -> verificationModel | None:
        stmt = (
            select(verificationModel)
            .where(verificationModel.user_id == user_id)
            .where(verificationModel.verification_type == verification_type)
            .order_by(verificationModel.created_at.desc())
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_valid_by_user_and_type(
        self,
        user_id: str,
        verification_type: verificationTypeEnum,
    ) -> verificationModel | None:
        now = datetime.now(timezone.utc)
        stmt = (
            select(verificationModel)
            .where(verificationModel.user_id == user_id)
            .where(verificationModel.verification_type == verification_type)
            .where(verificationModel.used == False)
            .where(verificationModel.expires_at > now)
            .order_by(verificationModel.created_at.desc())
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_valid_by_hash(
        self,
        code_hash: str,
        verification_type: verificationTypeEnum,
    ) -> verificationModel | None:
        now = datetime.now(timezone.utc)
        stmt = (
            select(verificationModel)
            .where(verificationModel.code_hash == code_hash)
            .where(verificationModel.verification_type == verification_type)
            .where(verificationModel.used == False)
            .where(verificationModel.expires_at > now)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def save(self, verification: verificationModel) -> verificationModel:
        self._session.add(verification)
        await self._session.flush()
        await self._session.refresh(verification)
        return verification

    async def update(self, verification: verificationModel) -> verificationModel:
        self._session.add(verification)
        await self._session.flush()
        await self._session.refresh(verification)
        return verification

    async def delete_expired(self, before: datetime) -> int:
        stmt = delete(verificationModel).where(verificationModel.expires_at < before)
        result = await self._session.execute(stmt)
        return result.rowcount

    async def invalidate_previous(
        self,
        user_id: str,
        verification_type: verificationTypeEnum,
    ) -> int:
        stmt = (
            update(verificationModel)
            .where(verificationModel.user_id == user_id)
            .where(verificationModel.verification_type == verification_type)
            .where(verificationModel.used == False)
            .values(used=True)
        )
        result = await self._session.execute(stmt)
        return result.rowcount
