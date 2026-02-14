from __future__ import annotations

from typing import TYPE_CHECKING

from sqlmodel import select

from src.application.interfaces.ApiKeyRepositoryInterface import apiKeyRepositoryInterface
from src.domain.enums.ApiKeyStatusEnum import apiKeyStatusEnum
from src.domain.models.ApiKeyModel import apiKeyModel

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class apiKeyRepository(apiKeyRepositoryInterface):

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def find_by_prefix(self, prefix: str) -> apiKeyModel | None:
        stmt = select(apiKeyModel).where(apiKeyModel.key_prefix == prefix)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_by_id(self, key_id: str) -> apiKeyModel | None:
        stmt = select(apiKeyModel).where(apiKeyModel.id == key_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_by_service(self, service_name: str) -> list[apiKeyModel]:
        stmt = (
            select(apiKeyModel)
            .where(apiKeyModel.service_name == service_name)
            .where(apiKeyModel.status == apiKeyStatusEnum.ACTIVE)
            .order_by(apiKeyModel.created_at.desc())
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def save(self, api_key: apiKeyModel) -> apiKeyModel:
        self._session.add(api_key)
        await self._session.flush()
        await self._session.refresh(api_key)
        return api_key

    async def update(self, api_key: apiKeyModel) -> apiKeyModel:
        self._session.add(api_key)
        await self._session.flush()
        await self._session.refresh(api_key)
        return api_key
