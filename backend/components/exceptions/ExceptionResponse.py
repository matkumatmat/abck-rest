from __future__ import annotations

from datetime import datetime, timezone

from pydantic import BaseModel, ConfigDict, Field


class exceptionResponse(BaseModel):
    success: bool = False
    c: str = Field(alias="_c")
    m: str = Field(alias="_m")
    ts: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat(), alias="_ts")
    d: dict | None = Field(default=None, alias="_d")

    model_config = ConfigDict(
        populate_by_name=True,
    )

    @classmethod
    def create(
        cls,
        code: str,
        message: str,
        detail: dict | None = None,
    ) -> exceptionResponse:
        return cls(
            c=code,
            m=message,
            d=detail,
        )
