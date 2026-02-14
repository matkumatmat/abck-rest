from __future__ import annotations

import base64
from typing import TYPE_CHECKING, Any, TypeVar

from sqlalchemy import asc, desc
from sqlmodel import select

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession
    from sqlmodel import SQLModel

T = TypeVar("T", bound="SQLModel")


class cursorPagination:

    def __init__(self, default_limit: int = 20, max_limit: int = 100) -> None:
        self._default_limit = default_limit
        self._max_limit = max_limit

    @staticmethod
    def encode_cursor(value: Any) -> str:
        return base64.urlsafe_b64encode(str(value).encode()).decode()

    @staticmethod
    def decode_cursor(cursor: str) -> str:
        try:
            return base64.urlsafe_b64decode(cursor.encode()).decode()
        except Exception:
            return ""

    async def paginate(
        self,
        session: AsyncSession,
        model: type[T],
        cursor: str | None = None,
        limit: int | None = None,
        order_column: str = "id",
        ascending: bool = True,
    ) -> tuple[list[T], str | None, bool]:
        limit = min(limit or self._default_limit, self._max_limit)
        column = getattr(model, order_column)
        order_fn = asc if ascending else desc

        stmt = select(model).order_by(order_fn(column))

        if cursor:
            decoded_cursor = self.decode_cursor(cursor)
            if decoded_cursor:
                if ascending:
                    stmt = stmt.where(column > decoded_cursor)
                else:
                    stmt = stmt.where(column < decoded_cursor)

        stmt = stmt.limit(limit + 1)
        result = await session.execute(stmt)
        items = list(result.scalars().all())

        has_next = len(items) > limit
        if has_next:
            items = items[:limit]

        next_cursor = None
        if has_next and items:
            last_item = items[-1]
            last_value = getattr(last_item, order_column)
            next_cursor = self.encode_cursor(last_value)

        return items, next_cursor, has_next
