from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime

from src.domain.models.PasswordResetModel import passwordResetModel


class passwordResetRepositoryInterface(ABC):

    @abstractmethod
    async def find_by_hash(self, token_hash: str) -> passwordResetModel | None: ...

    @abstractmethod
    async def find_valid_by_user(self, user_id: str) -> passwordResetModel | None: ...

    @abstractmethod
    async def save(self, reset: passwordResetModel) -> passwordResetModel: ...

    @abstractmethod
    async def update(self, reset: passwordResetModel) -> passwordResetModel: ...

    @abstractmethod
    async def delete_expired(self, before: datetime) -> int: ...

    @abstractmethod
    async def invalidate_previous(self, user_id: str) -> int: ...
