from __future__ import annotations

import secrets
from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING

from components.crypto.CryptoFactory import cryptoFactory
from components.exceptions.BaseException import (
    badRequestException,
    notFoundException,
)
from components.logger.LoggerFactory import loggerFactory
from src.application.interfaces.UnitOfWorkInterface import unitOfWorkInterface
from src.domain.enums.UserStatusEnum import userStatusEnum
from src.domain.enums.VerificationTypeEnum import verificationTypeEnum
from src.domain.models.PasswordResetModel import passwordResetModel
from src.domain.models.VerificationModel import verificationModel

if TYPE_CHECKING:
    from fastapi import BackgroundTasks

    from components.email.EmailService import emailService
    from src.application.services.SessionService import sessionService
    from src.application.services.TokenService import tokenService
    from src.domain.config.Settings import settings


class verificationService:

    def __init__(
        self,
        config: settings,
        uow: unitOfWorkInterface,
        crypto: cryptoFactory,
        session_service: sessionService,
        token_service: tokenService,
        email_service: emailService,
    ) -> None:
        self._config = config
        self._uow = uow
        self._crypto = crypto
        self._session_service = session_service
        self._token_service = token_service
        self._email_service = email_service
        self._logger = loggerFactory.create("verification_service")

    async def create_email_verification(
        self,
        user_id: str,
        background_tasks: BackgroundTasks,
    ) -> None:
        token = self._generate_token()
        token_hash = self._crypto.hash_data_hex(token)

        async with self._uow as uow:
            user = await uow.users.find_by_id(user_id)
            if user is None:
                raise notFoundException("User not found")

            if user.status == userStatusEnum.ACTIVE:
                raise badRequestException("Email already verified")

            await uow.verifications.invalidate_previous(user_id, verificationTypeEnum.EMAIL_VERIFY)

            verification = verificationModel(
                user_id=user_id,
                code_hash=token_hash,
                verification_type=verificationTypeEnum.EMAIL_VERIFY,
                expires_at=datetime.now(timezone.utc) + timedelta(seconds=self._config.verification_expires),
            )
            await uow.verifications.save(verification)
            await uow.commit()

            user_email = user.email
            user_name = user.name

        verification_link = f"{self._config.frontend_url}/verify-email?token={token}"

        background_tasks.add_task(
            self._email_service.send,
            to=user_email,
            template_name="EmailVerification",
            user_name=user_name,
            verification_link=verification_link,
            expires_in="1 hour",
        )

        self._logger.info("email_verification_created", user_id=user_id)

    async def verify_email(
        self,
        token: str,
        background_tasks: BackgroundTasks,
    ) -> None:
        token_hash = self._crypto.hash_data_hex(token)

        async with self._uow as uow:
            verification = await uow.verifications.find_valid_by_hash(
                token_hash,
                verificationTypeEnum.EMAIL_VERIFY,
            )

            if verification is None:
                raise badRequestException("Invalid or expired verification token")

            if not verification.is_valid():
                raise badRequestException("Verification token expired")

            verification.mark_used()

            user = await uow.users.find_by_id(verification.user_id)
            if user is None:
                raise notFoundException("User not found")

            user.activate()
            await uow.commit()

            user_email = user.email
            user_name = user.name
            user_id = user.id

        background_tasks.add_task(
            self._email_service.send,
            to=user_email,
            template_name="Welcome",
            user_name=user_name,
            app_name=self._config.app_name,
        )

        self._logger.info("email_verified", user_id=user_id)

    async def create_password_reset(
        self,
        email: str,
        background_tasks: BackgroundTasks,
    ) -> None:
        async with self._uow as uow:
            user = await uow.users.find_by_email(email.lower().strip())

            if user is None:
                self._logger.warning("password_reset_requested_unknown_email", email=email)
                return

            if user.status != userStatusEnum.ACTIVE:
                self._logger.warning("password_reset_inactive_user", user_id=user.id)
                return

            await uow.password_resets.invalidate_previous(user.id)

            token = self._generate_token()
            token_hash = self._crypto.hash_data_hex(token)

            reset = passwordResetModel(
                user_id=user.id,
                token_hash=token_hash,
                expires_at=datetime.now(timezone.utc) + timedelta(seconds=self._config.password_reset_expires),
            )
            await uow.password_resets.save(reset)
            await uow.commit()

            user_email = user.email
            user_name = user.name

        reset_link = f"{self._config.frontend_url}/reset-password?token={token}"

        background_tasks.add_task(
            self._email_service.send,
            to=user_email,
            template_name="PasswordReset",
            user_name=user_name,
            reset_link=reset_link,
            expires_in="30 minutes",
        )

        self._logger.info("password_reset_created", user_id=user.id)

    async def reset_password(self, token: str, new_password: str) -> None:
        token_hash = self._crypto.hash_data_hex(token)

        async with self._uow as uow:
            reset = await uow.password_resets.find_by_hash(token_hash)

            if reset is None or not reset.is_valid():
                raise badRequestException("Invalid or expired reset token")

            reset.mark_used()

            user = await uow.users.find_by_id(reset.user_id)
            if user is None:
                raise notFoundException("User not found")

            new_hash = self._crypto.hash_password(new_password)
            user.update_password(new_hash)
            await uow.commit()

            user_id = user.id

        await self._session_service.revoke_all_sessions(user_id)
        await self._token_service.revoke_by_user(user_id)

        self._logger.info("password_reset_completed", user_id=user_id)

    def _generate_token(self) -> str:
        return secrets.token_urlsafe(32)
