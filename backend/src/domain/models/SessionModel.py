from __future__ import annotations

from datetime import datetime, timezone

import sqlalchemy as sa
from sqlmodel import Field

from src.domain.enums.SessionStatusEnum import sessionStatusEnum
from src.domain.models.BaseModel import _utc_now, baseModel


class sessionModel(baseModel, table=True):
    __tablename__ = "sessions"

    user_id: str = Field(foreign_key="users.id", index=True, max_length=36)
    ip_address: str = Field(max_length=45)
    user_agent: str = Field(max_length=512)
    status: sessionStatusEnum = Field(default=sessionStatusEnum.ACTIVE)
    expires_at: datetime = Field(sa_type=sa.DateTime(timezone=True))
    last_activity: datetime = Field(default_factory=_utc_now, sa_type=sa.DateTime(timezone=True))

    def is_expired(self) -> bool:
        return datetime.now(timezone.utc) > self.expires_at

    def is_active(self) -> bool:
        return self.status == sessionStatusEnum.ACTIVE and not self.is_expired()

    def __bool__(self) -> bool:
        return self.is_active()

    def revoke(self) -> None:
        self.status = sessionStatusEnum.REVOKED
        self.touch()

    def refresh_activity(self) -> None:
        self.last_activity = _utc_now()
        self.touch()

    def extend(self, duration_seconds: int) -> None:
        from datetime import timedelta

        self.expires_at = datetime.now(timezone.utc) + timedelta(seconds=duration_seconds)
        self.touch()
