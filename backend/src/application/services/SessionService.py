from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING

from components.database.RedisEngine import redisEngine
from components.exceptions.BaseException import forbiddenException, notFoundException
from components.logger.LoggerFactory import loggerFactory
from src.application.interfaces.UnitOfWorkInterface import unitOfWorkInterface
from src.domain.enums.SessionStatusEnum import sessionStatusEnum
from src.domain.models.SessionModel import sessionModel

if TYPE_CHECKING:
    from src.application.services.TokenService import tokenService
    from src.domain.config.Settings import settings


class sessionService:

    def __init__(
        self,
        config: settings,
        uow: unitOfWorkInterface,
        redis: redisEngine,
        token_service: tokenService,
    ) -> None:
        self._config = config
        self._uow = uow
        self._redis = redis
        self._token_service = token_service
        self._logger = loggerFactory.create("session_service")

    async def create_session(
        self,
        user_id: str,
        ip_address: str,
        user_agent: str,
    ) -> sessionModel:
        expires_at = datetime.now(timezone.utc) + timedelta(seconds=self._config.session_expires)

        session = sessionModel(
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent[:512] if len(user_agent) > 512 else user_agent,
            status=sessionStatusEnum.ACTIVE,
            expires_at=expires_at,
        )

        async with self._uow as uow:
            active_count = await uow.sessions.count_active_by_user_id(user_id)

            if active_count >= self._config.session_max_per_user:
                oldest_sessions = await uow.sessions.find_active_by_user_id(user_id)
                if oldest_sessions:
                    oldest = oldest_sessions[-1]
                    oldest.revoke()

            await uow.sessions.save(session)
            await uow.commit()

        await self._redis.set(
            f"session:{session.id}",
            {
                "user_id": user_id,
                "ip": ip_address,
                "ua": user_agent[:512],
                "exp": expires_at.isoformat(),
            },
            ttl=self._config.session_expires,
        )

        return session

    async def list_sessions(self, user_id: str) -> list[sessionModel]:
        async with self._uow as uow:
            sessions = await uow.sessions.find_active_by_user_id(user_id)
        return [s for s in sessions if s.is_active()]

    async def revoke_session(self, user_id: str, session_id: str) -> None:
        async with self._uow as uow:
            session = await uow.sessions.find_by_id(session_id)

            if session is None:
                raise notFoundException("Session not found")

            if session.user_id != user_id:
                raise forbiddenException("Cannot revoke session owned by another user")

            session.revoke()
            await uow.refresh_tokens.revoke_by_session(session_id)
            await uow.commit()

        await self._redis.delete(f"session:{session_id}")

    async def revoke_session_internal(self, session_id: str) -> None:
        async with self._uow as uow:
            session = await uow.sessions.find_by_id(session_id)
            if session is not None:
                session.revoke()
                await uow.refresh_tokens.revoke_by_session(session_id)
                await uow.commit()

        await self._redis.delete(f"session:{session_id}")

    async def revoke_all_sessions(self, user_id: str) -> int:
        async with self._uow as uow:
            sessions = await uow.sessions.find_active_by_user_id(user_id)
            count = 0

            for session in sessions:
                session.revoke()
                await uow.refresh_tokens.revoke_by_session(session.id)
                await self._redis.delete(f"session:{session.id}")
                count += 1

            await uow.commit()

        return count

    async def validate_session(self, session_id: str) -> str | None:
        cached = await self._redis.get(f"session:{session_id}")
        if cached and isinstance(cached, dict):
            return cached.get("user_id")

        async with self._uow as uow:
            session = await uow.sessions.find_by_id(session_id)

            if session is None or not session.is_active():
                return None

            session.refresh_activity()
            await uow.commit()

        await self._redis.set(
            f"session:{session.id}",
            {
                "user_id": session.user_id,
                "ip": session.ip_address,
                "ua": session.user_agent,
                "exp": session.expires_at.isoformat(),
            },
            ttl=self._config.session_expires,
        )

        return session.user_id
