from __future__ import annotations

from datetime import datetime, timezone

import sqlalchemy as sa
from sqlmodel import Field

from src.domain.models.BaseModel import baseModel


class passwordResetModel(baseModel, table=True):
    __tablename__ = "password_resets"

    user_id: str = Field(foreign_key="users.id", index=True, max_length=36)
    token_hash: str = Field(unique=True, max_length=128)
    expires_at: datetime = Field(sa_type=sa.DateTime(timezone=True))
    used: bool = Field(default=False)

    def is_valid(self) -> bool:
        return not self.used and datetime.now(timezone.utc) < self.expires_at

    def __bool__(self) -> bool:
        return self.is_valid()

    def mark_used(self) -> None:
        self.used = True
        self.touch()
