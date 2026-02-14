from __future__ import annotations

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class paginationMeta(BaseModel):
    total: int
    page: int | None = None
    per_page: int | None = None
    cursor: str | None = None
    has_next: bool = False
    has_prev: bool = False

    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=to_camel,
    )
