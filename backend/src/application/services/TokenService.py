from __future__ import annotations

import time
from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING

import jwt

from components.crypto.CryptoFactory import cryptoFactory
from components.database.RedisEngine import redisEngine
from components.exceptions.BaseException import unauthorizedException
from components.logger.LoggerFactory import loggerFactory
from components.uuid.UuidGenerator import uuidGenerator
from src.application.interfaces.UnitOfWorkInterface import unitOfWorkInterface
from src.domain.models.RefreshTokenModel import refreshTokenModel
from src.domain.types.TokenPayload import tokenPayload

if TYPE_CHECKING:
    from src.domain.config.Settings import settings


class tokenService:

    def __init__(
        self,
        config: settings,
        uow: unitOfWorkInterface,
        redis: redisEngine,
        crypto: cryptoFactory,
    ) -> None:
        self._config = config
        self._uow = uow
        self._redis = redis
        self._crypto = crypto
        self._logger = loggerFactory.create("token_service")

    async def generate_pair(
        self,
        user_id: str,
        session_id: str,
    ) -> tuple[str, str, int]:
        now = int(time.time())
        access_jti = uuidGenerator.create()
        access_exp = now + self._config.jwt_access_expires
        refresh_exp = now + self._config.jwt_refresh_expires

        access_payload = tokenPayload(
            sub=user_id,
            sid=session_id,
            jti=access_jti,
            exp=access_exp,
            iat=now,
            typ="access",
        )

        access_token = jwt.encode(
            access_payload.to_dict(),
            self._config.jwt_secret,
            algorithm=self._config.jwt_algorithm,
        )

        refresh_token = uuidGenerator.create()
        refresh_hash = self._crypto.hash_data_hex(refresh_token)

        async with self._uow as uow:
            token_model = refreshTokenModel(
                user_id=user_id,
                token_hash=refresh_hash,
                session_id=session_id,
                expires_at=datetime.fromtimestamp(refresh_exp, tz=timezone.utc),
            )
            await uow.refresh_tokens.save(token_model)
            await uow.commit()

        return access_token, refresh_token, self._config.jwt_access_expires

    async def refresh(self, refresh_token: str) -> tuple[str, str, int]:
        refresh_hash = self._crypto.hash_data_hex(refresh_token)

        async with self._uow as uow:
            token = await uow.refresh_tokens.find_by_hash(refresh_hash)

            if token is None or not token.is_valid():
                raise unauthorizedException("Invalid or expired refresh token")

            session = await uow.sessions.find_by_id(token.session_id)
            if session is None or not session.is_active():
                raise unauthorizedException("Session no longer active")

            token.revoke()
            await uow.commit()

        return await self.generate_pair(token.user_id, token.session_id)

    def decode_access(self, token: str) -> tokenPayload:
        try:
            payload = jwt.decode(
                token,
                self._config.jwt_secret,
                algorithms=[self._config.jwt_algorithm],
            )
        except jwt.ExpiredSignatureError:
            raise unauthorizedException("Token expired")
        except jwt.InvalidTokenError:
            raise unauthorizedException("Invalid token")

        return tokenPayload.from_dict(payload)

    async def validate_access(self, token: str) -> tokenPayload:
        payload = self.decode_access(token)

        if await self.is_blacklisted(payload.jti):
            raise unauthorizedException("Token has been revoked")

        return payload

    async def blacklist_access(self, jti: str, expires_at: int) -> None:
        remaining = expires_at - int(time.time())
        if remaining > 0:
            await self._redis.set(
                f"jwt_blacklist:{jti}",
                "1",
                ttl=remaining,
            )

    async def is_blacklisted(self, jti: str) -> bool:
        return await self._redis.exists(f"jwt_blacklist:{jti}")

    async def revoke_by_session(self, session_id: str) -> None:
        async with self._uow as uow:
            tokens = await uow.refresh_tokens.find_by_session_id(session_id)
            for token in tokens:
                token.revoke()
            await uow.commit()

    async def revoke_by_user(self, user_id: str) -> None:
        async with self._uow as uow:
            await uow.refresh_tokens.revoke_by_user(user_id)
            await uow.commit()
