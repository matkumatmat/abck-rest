from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime

from src.domain.models.SessionModel import sessionModel


class sessionRepositoryInterface(ABC):

    @abstractmethod
    async def find_by_id(self, session_id: str) -> sessionModel | None: ...

    @abstractmethod
    async def find_by_user_id(self, user_id: str) -> list[sessionModel]: ...

    @abstractmethod
    async def find_active_by_user_id(self, user_id: str) -> list[sessionModel]: ...

    @abstractmethod
    async def count_active_by_user_id(self, user_id: str) -> int: ...

    @abstractmethod
    async def save(self, session: sessionModel) -> sessionModel: ...

    @abstractmethod
    async def update(self, session: sessionModel) -> sessionModel: ...

    @abstractmethod
    async def delete_expired(self, before: datetime) -> int: ...
