from __future__ import annotations

from datetime import datetime, timezone

import sqlalchemy as sa
from sqlmodel import Field

from src.domain.enums.VerificationTypeEnum import verificationTypeEnum
from src.domain.models.BaseModel import baseModel


class verificationModel(baseModel, table=True):
    __tablename__ = "verifications"

    user_id: str = Field(foreign_key="users.id", index=True, max_length=36)
    code_hash: str = Field(max_length=128)
    verification_type: verificationTypeEnum
    expires_at: datetime = Field(sa_type=sa.DateTime(timezone=True))
    used: bool = Field(default=False)

    def is_valid(self) -> bool:
        return not self.used and datetime.now(timezone.utc) < self.expires_at

    def __bool__(self) -> bool:
        return self.is_valid()

    def mark_used(self) -> None:
        self.used = True
        self.touch()
