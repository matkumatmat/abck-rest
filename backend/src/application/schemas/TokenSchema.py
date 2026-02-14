from __future__ import annotations

from pydantic import Field

from components.schemas.BaseResponse import baseRequest, baseResponse


class refreshTokenRequest(baseRequest):
    refresh_token: str = Field(min_length=1)


class tokenResponse(baseResponse):
    at: str = Field(alias="_at")
    rt: str = Field(alias="_rt")
    exp: int = Field(alias="_exp")
