from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime

from src.domain.enums.VerificationTypeEnum import verificationTypeEnum
from src.domain.models.VerificationModel import verificationModel


class verificationRepositoryInterface(ABC):

    @abstractmethod
    async def find_by_user_and_type(
        self,
        user_id: str,
        verification_type: verificationTypeEnum,
    ) -> verificationModel | None: ...

    @abstractmethod
    async def find_valid_by_user_and_type(
        self,
        user_id: str,
        verification_type: verificationTypeEnum,
    ) -> verificationModel | None: ...

    @abstractmethod
    async def find_valid_by_hash(
        self,
        code_hash: str,
        verification_type: verificationTypeEnum,
    ) -> verificationModel | None: ...

    @abstractmethod
    async def save(self, verification: verificationModel) -> verificationModel: ...

    @abstractmethod
    async def update(self, verification: verificationModel) -> verificationModel: ...

    @abstractmethod
    async def delete_expired(self, before: datetime) -> int: ...

    @abstractmethod
    async def invalidate_previous(
        self,
        user_id: str,
        verification_type: verificationTypeEnum,
    ) -> int: ...
