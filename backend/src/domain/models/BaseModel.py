from __future__ import annotations

from datetime import datetime, timezone

import sqlalchemy as sa
from sqlmodel import Field, SQLModel

from components.uuid.UuidGenerator import uuidGenerator


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class baseModel(SQLModel):
    id: str = Field(default_factory=uuidGenerator.create, primary_key=True)
    created_at: datetime = Field(
        default_factory=_utc_now,
        sa_type=sa.DateTime(timezone=True),
    )
    updated_at: datetime = Field(
        default_factory=_utc_now,
        sa_type=sa.DateTime(timezone=True),
    )

    def touch(self) -> None:
        self.updated_at = _utc_now()

    def apply_update(self, data: dict) -> None:
        for key, value in data.items():
            if value is not None and hasattr(self, key):
                setattr(self, key, value)
        self.touch()
