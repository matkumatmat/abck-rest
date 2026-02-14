from __future__ import annotations

import secrets
from typing import TYPE_CHECKING

from components.crypto.CryptoFactory import cryptoFactory
from components.database.RedisEngine import redisEngine
from components.exceptions.BaseException import (
    alreadyExistsException,
    rateLimitedException,
    unauthorizedException,
)
from components.logger.LoggerFactory import loggerFactory
from src.application.interfaces.UnitOfWorkInterface import unitOfWorkInterface
from src.domain.enums.VerificationTypeEnum import verificationTypeEnum
from src.domain.models.UserModel import userModel
from src.domain.models.VerificationModel import verificationModel

if TYPE_CHECKING:
    from datetime import datetime, timedelta, timezone

    from fastapi import BackgroundTasks

    from components.email.EmailService import emailService
    from src.application.services.SessionService import sessionService
    from src.application.services.TokenService import tokenService
    from src.domain.config.Settings import settings


class authService:

    def __init__(
        self,
        config: settings,
        uow: unitOfWorkInterface,
        redis: redisEngine,
        crypto: cryptoFactory,
        session_service: sessionService,
        token_service: tokenService,
        email_service: emailService,
    ) -> None:
        self._config = config
        self._uow = uow
        self._redis = redis
        self._crypto = crypto
        self._session_service = session_service
        self._token_service = token_service
        self._email_service = email_service
        self._logger = loggerFactory.create("auth_service")

    async def register(
        self,
        email: str,
        password: str,
        name: str,
        background_tasks: BackgroundTasks,
    ) -> userModel:
        async with self._uow as uow:
            if await uow.users.email_exists(email):
                raise alreadyExistsException("Email already registered")

            password_hash = self._crypto.hash_password(password)
            user = userModel(
                email=email.lower().strip(),
                password_hash=password_hash,
                name=name.strip(),
            )
            await uow.users.save(user)

            token = self._generate_verification_token()
            token_hash = self._crypto.hash_data_hex(token)

            from datetime import datetime, timedelta, timezone

            verification = verificationModel(
                user_id=user.id,
                code_hash=token_hash,
                verification_type=verificationTypeEnum.EMAIL_VERIFY,
                expires_at=datetime.now(timezone.utc) + timedelta(seconds=self._config.verification_expires),
            )
            await uow.verifications.save(verification)
            await uow.commit()

        verification_link = f"{self._config.frontend_url}/verify-email?token={token}"

        background_tasks.add_task(
            self._email_service.send,
            to=user.email,
            template_name="EmailVerification",
            user_name=user.name,
            verification_link=verification_link,
            expires_in="1 hour",
        )

        self._logger.info("user_registered", user_id=user.id, email=user.email)
        return user

    async def login(
        self,
        email: str,
        password: str,
        ip_address: str,
        user_agent: str,
    ) -> tuple[str, str, int, str]:
        await self._check_rate_limit(email)

        async with self._uow as uow:
            user = await uow.users.find_by_email(email.lower().strip())

            if user is None:
                await self._record_failed_login(email)
                raise unauthorizedException("Invalid credentials")

            if not self._crypto.verify_password(password, user.password_hash):
                await self._record_failed_login(email)
                raise unauthorizedException("Invalid credentials")

            if not user.is_active():
                raise unauthorizedException("Account is not active")

        await self._reset_rate_limit(email)

        session = await self._session_service.create_session(user.id, ip_address, user_agent)
        access_token, refresh_token, expires_in = await self._token_service.generate_pair(user.id, session.id)

        csrf_token = self._generate_csrf_token(session.id)

        self._logger.info("user_login", user_id=user.id, session_id=session.id, ip=ip_address)
        return access_token, refresh_token, expires_in, csrf_token

    async def logout(self, session_id: str, access_jti: str, access_exp: int) -> None:
        await self._session_service.revoke_session_internal(session_id)
        await self._token_service.blacklist_access(access_jti, access_exp)
        self._logger.info("user_logout", session_id=session_id)

    async def _check_rate_limit(self, email: str) -> None:
        key = f"login:{email}:{self._current_window()}"
        count = await self._redis.get(key)

        if count is not None and int(count) >= self._config.login_rate_limit_max:
            raise rateLimitedException("Too many login attempts. Please try again later.")

    async def _record_failed_login(self, email: str) -> None:
        key = f"login:{email}:{self._current_window()}"
        await self._redis.incr(key)
        await self._redis.expire(key, self._config.login_rate_limit_window)

    async def _reset_rate_limit(self, email: str) -> None:
        key = f"login:{email}:{self._current_window()}"
        await self._redis.delete(key)

    def _current_window(self) -> int:
        import time

        return int(time.time()) // self._config.login_rate_limit_window

    def _generate_verification_token(self) -> str:
        return secrets.token_urlsafe(32)

    def _generate_csrf_token(self, session_id: str) -> str:
        return self._crypto.sign_hex(session_id)
