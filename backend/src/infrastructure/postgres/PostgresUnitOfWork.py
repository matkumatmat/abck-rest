from __future__ import annotations

from typing import TYPE_CHECKING, Self

from src.application.interfaces.UnitOfWorkInterface import unitOfWorkInterface
from src.infrastructure.repositories.ApiKeyRepository import apiKeyRepository
from src.infrastructure.repositories.PasswordResetRepository import passwordResetRepository
from src.infrastructure.repositories.RefreshTokenRepository import refreshTokenRepository
from src.infrastructure.repositories.SessionRepository import sessionRepository
from src.infrastructure.repositories.UserRepository import userRepository
from src.infrastructure.repositories.VerificationRepository import verificationRepository

if TYPE_CHECKING:
    from collections.abc import Callable

    from sqlalchemy.ext.asyncio import AsyncSession


class postgresUnitOfWork(unitOfWorkInterface):

    def __init__(self, session_factory: Callable[[], AsyncSession]) -> None:
        self._session_factory = session_factory
        self._session: AsyncSession | None = None

    async def __aenter__(self) -> Self:
        self._session = self._session_factory()
        self.users = userRepository(self._session)
        self.sessions = sessionRepository(self._session)
        self.refresh_tokens = refreshTokenRepository(self._session)
        self.verifications = verificationRepository(self._session)
        self.password_resets = passwordResetRepository(self._session)
        self.api_keys = apiKeyRepository(self._session)
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: object,
    ) -> None:
        if exc_type is not None:
            await self.rollback()
        if self._session is not None:
            await self._session.close()
            self._session = None

    async def commit(self) -> None:
        if self._session is not None:
            await self._session.commit()

    async def rollback(self) -> None:
        if self._session is not None:
            await self._session.rollback()
