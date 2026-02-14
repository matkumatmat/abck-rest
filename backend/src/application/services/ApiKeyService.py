from __future__ import annotations

import secrets
from datetime import datetime
from typing import TYPE_CHECKING

from components.crypto.CryptoFactory import cryptoFactory
from components.exceptions.BaseException import notFoundException, unauthorizedException
from components.logger.LoggerFactory import loggerFactory
from src.application.interfaces.UnitOfWorkInterface import unitOfWorkInterface
from src.domain.models.ApiKeyModel import apiKeyModel

if TYPE_CHECKING:
    from src.domain.config.Settings import settings


class apiKeyService:

    def __init__(
        self,
        config: settings,
        uow: unitOfWorkInterface,
        crypto: cryptoFactory,
    ) -> None:
        self._config = config
        self._uow = uow
        self._crypto = crypto
        self._logger = loggerFactory.create("api_key_service")

    async def create(
        self,
        name: str,
        service_name: str,
        expires_at: datetime | None = None,
    ) -> tuple[str, str]:
        key = self._generate_key()
        prefix = key[: self._config.api_key_prefix_length]
        key_hash = self._crypto.hash_data_hex(key)

        api_key = apiKeyModel(
            name=name.strip(),
            key_hash=key_hash,
            key_prefix=prefix,
            service_name=service_name.strip(),
            expires_at=expires_at,
        )

        async with self._uow as uow:
            await uow.api_keys.save(api_key)
            await uow.commit()

        self._logger.info(
            "api_key_created",
            key_id=api_key.id,
            prefix=prefix,
            service_name=service_name,
        )

        return key, prefix

    async def validate(self, api_key: str) -> tuple[str, str]:
        if len(api_key) < self._config.api_key_prefix_length:
            raise unauthorizedException("Invalid API key format")

        prefix = api_key[: self._config.api_key_prefix_length]
        key_hash = self._crypto.hash_data_hex(api_key)

        async with self._uow as uow:
            key_model = await uow.api_keys.find_by_prefix(prefix)

            if key_model is None:
                raise unauthorizedException("Invalid API key")

            if key_model.key_hash != key_hash:
                raise unauthorizedException("Invalid API key")

            if not key_model.is_valid():
                raise unauthorizedException("API key expired or revoked")

            key_model.record_usage()
            await uow.commit()

            service_name = key_model.service_name
            key_id = key_model.id

        self._logger.info("api_key_validated", key_id=key_id, service_name=service_name)
        return key_id, service_name

    async def revoke(self, key_id: str) -> None:
        async with self._uow as uow:
            key_model = await uow.api_keys.find_by_id(key_id)

            if key_model is None:
                raise notFoundException("API key not found")

            key_model.revoke()
            await uow.commit()

        self._logger.info("api_key_revoked", key_id=key_id)

    async def list_by_service(self, service_name: str) -> list[apiKeyModel]:
        async with self._uow as uow:
            keys = await uow.api_keys.find_by_service(service_name)
        return keys

    async def get_by_id(self, key_id: str) -> apiKeyModel | None:
        async with self._uow as uow:
            key = await uow.api_keys.find_by_id(key_id)
        return key

    def _generate_key(self) -> str:
        return secrets.token_urlsafe(self._config.api_key_length)
