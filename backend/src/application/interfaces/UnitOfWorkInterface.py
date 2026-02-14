from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Self

from src.application.interfaces.ApiKeyRepositoryInterface import apiKeyRepositoryInterface
from src.application.interfaces.PasswordResetRepositoryInterface import passwordResetRepositoryInterface
from src.application.interfaces.RefreshTokenRepositoryInterface import refreshTokenRepositoryInterface
from src.application.interfaces.SessionRepositoryInterface import sessionRepositoryInterface
from src.application.interfaces.UserRepositoryInterface import userRepositoryInterface
from src.application.interfaces.VerificationRepositoryInterface import verificationRepositoryInterface


class unitOfWorkInterface(ABC):
    users: userRepositoryInterface
    sessions: sessionRepositoryInterface
    refresh_tokens: refreshTokenRepositoryInterface
    verifications: verificationRepositoryInterface
    password_resets: passwordResetRepositoryInterface
    api_keys: apiKeyRepositoryInterface

    @abstractmethod
    async def __aenter__(self) -> Self: ...

    @abstractmethod
    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: object,
    ) -> None: ...

    @abstractmethod
    async def commit(self) -> None: ...

    @abstractmethod
    async def rollback(self) -> None: ...
