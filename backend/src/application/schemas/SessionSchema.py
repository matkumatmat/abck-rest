from __future__ import annotations

from datetime import datetime

from pydantic import Field

from components.schemas.BaseResponse import baseRequest, baseResponse


class revokeSessionRequest(baseRequest):
    session_id: str = Field(min_length=36, max_length=36)


class sessionItemResponse(baseResponse):
    sid: str = Field(alias="_sid")
    ip: str = Field(alias="_ip")
    ua: str = Field(alias="_ua")
    la: datetime = Field(alias="_la")
    ca: datetime = Field(alias="_ca")


class sessionListResponse(baseResponse):
    sessions: list[sessionItemResponse]
    total: int
