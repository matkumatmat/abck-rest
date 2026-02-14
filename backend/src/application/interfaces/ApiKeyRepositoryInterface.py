from __future__ import annotations

from abc import ABC, abstractmethod

from src.domain.models.ApiKeyModel import apiKeyModel


class apiKeyRepositoryInterface(ABC):

    @abstractmethod
    async def find_by_prefix(self, prefix: str) -> apiKeyModel | None: ...

    @abstractmethod
    async def find_by_id(self, key_id: str) -> apiKeyModel | None: ...

    @abstractmethod
    async def find_by_service(self, service_name: str) -> list[apiKeyModel]: ...

    @abstractmethod
    async def save(self, api_key: apiKeyModel) -> apiKeyModel: ...

    @abstractmethod
    async def update(self, api_key: apiKeyModel) -> apiKeyModel: ...
