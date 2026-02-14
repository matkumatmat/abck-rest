from __future__ import annotations

from abc import ABC, abstractmethod

from src.domain.models.UserModel import userModel


class userRepositoryInterface(ABC):

    @abstractmethod
    async def find_by_id(self, user_id: str) -> userModel | None: ...

    @abstractmethod
    async def find_by_email(self, email: str) -> userModel | None: ...

    @abstractmethod
    async def save(self, user: userModel) -> userModel: ...

    @abstractmethod
    async def update(self, user: userModel) -> userModel: ...

    @abstractmethod
    async def email_exists(self, email: str) -> bool: ...
