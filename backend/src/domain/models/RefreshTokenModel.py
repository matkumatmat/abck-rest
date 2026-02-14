from __future__ import annotations

from datetime import datetime, timezone

import sqlalchemy as sa
from sqlmodel import Field

from src.domain.models.BaseModel import baseModel


class refreshTokenModel(baseModel, table=True):
    __tablename__ = "refresh_tokens"

    user_id: str = Field(foreign_key="users.id", index=True, max_length=36)
    token_hash: str = Field(unique=True, max_length=128)
    session_id: str = Field(foreign_key="sessions.id", index=True, max_length=36)
    expires_at: datetime = Field(sa_type=sa.DateTime(timezone=True))
    revoked: bool = Field(default=False)

    def is_valid(self) -> bool:
        return not self.revoked and datetime.now(timezone.utc) < self.expires_at

    def __bool__(self) -> bool:
        return self.is_valid()

    def revoke(self) -> None:
        self.revoked = True
        self.touch()
