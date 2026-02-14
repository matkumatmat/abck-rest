from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class baseResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        alias_generator=to_camel,
    )


class baseRequest(BaseModel):
    model_config = ConfigDict(strict=True)


class successResponse(BaseModel):
    success: bool = True
    data: Any = None
    meta: dict | None = None

    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=to_camel,
    )
