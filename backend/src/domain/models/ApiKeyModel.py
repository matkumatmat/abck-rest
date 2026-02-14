from __future__ import annotations

from datetime import datetime, timezone

import sqlalchemy as sa
from sqlmodel import Field

from src.domain.enums.ApiKeyStatusEnum import apiKeyStatusEnum
from src.domain.models.BaseModel import _utc_now, baseModel


class apiKeyModel(baseModel, table=True):
    __tablename__ = "api_keys"

    name: str = Field(max_length=100)
    key_hash: str = Field(unique=True, max_length=128)
    key_prefix: str = Field(max_length=16, index=True)
    service_name: str = Field(max_length=100)
    status: apiKeyStatusEnum = Field(default=apiKeyStatusEnum.ACTIVE)
    expires_at: datetime | None = Field(default=None, sa_type=sa.DateTime(timezone=True))
    last_used_at: datetime | None = Field(default=None, sa_type=sa.DateTime(timezone=True))

    def is_valid(self) -> bool:
        if self.status != apiKeyStatusEnum.ACTIVE:
            return False
        if self.expires_at is not None and datetime.now(timezone.utc) > self.expires_at:
            return False
        return True

    def __bool__(self) -> bool:
        return self.is_valid()

    def revoke(self) -> None:
        self.status = apiKeyStatusEnum.REVOKED
        self.touch()

    def record_usage(self) -> None:
        self.last_used_at = _utc_now()
        self.touch()
