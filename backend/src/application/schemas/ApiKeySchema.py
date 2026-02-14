from __future__ import annotations

from datetime import datetime

from pydantic import Field

from components.schemas.BaseResponse import baseRequest, baseResponse


class createApiKeyRequest(baseRequest):
    name: str = Field(min_length=1, max_length=100)
    service_name: str = Field(min_length=1, max_length=100)
    expires_at: datetime | None = None


class apiKeyCreatedResponse(baseResponse):
    k: str = Field(alias="_k")
    pfx: str = Field(alias="_pfx")
    name: str


class apiKeyItemResponse(baseResponse):
    kid: str = Field(alias="_kid")
    pfx: str = Field(alias="_pfx")
    name: str
    service_name: str
    lu: datetime | None = Field(default=None, alias="_lu")
    st: str = Field(alias="_st")


class apiKeyListResponse(baseResponse):
    keys: list[apiKeyItemResponse]
    total: int
