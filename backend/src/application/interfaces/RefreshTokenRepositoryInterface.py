from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime

from src.domain.models.RefreshTokenModel import refreshTokenModel


class refreshTokenRepositoryInterface(ABC):

    @abstractmethod
    async def find_by_hash(self, token_hash: str) -> refreshTokenModel | None: ...

    @abstractmethod
    async def find_by_session_id(self, session_id: str) -> list[refreshTokenModel]: ...

    @abstractmethod
    async def find_active_by_user_id(self, user_id: str) -> list[refreshTokenModel]: ...

    @abstractmethod
    async def save(self, token: refreshTokenModel) -> refreshTokenModel: ...

    @abstractmethod
    async def revoke_by_session(self, session_id: str) -> int: ...

    @abstractmethod
    async def revoke_by_user(self, user_id: str) -> int: ...

    @abstractmethod
    async def delete_expired(self, before: datetime) -> int: ...
