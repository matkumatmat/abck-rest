from __future__ import annotations

from typing import TYPE_CHECKING, TypeVar

from sqlalchemy import func, select

from components.schemas.PaginationSchema import paginationMeta

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession
    from sqlmodel import SQLModel

T = TypeVar("T", bound="SQLModel")


class offsetPagination:

    def __init__(self, default_limit: int = 20, max_limit: int = 100) -> None:
        self._default_limit = default_limit
        self._max_limit = max_limit

    @staticmethod
    def calculate_offset(page: int, per_page: int) -> int:
        return (max(page, 1) - 1) * per_page

    async def paginate(
        self,
        session: AsyncSession,
        model: type[T],
        page: int = 1,
        per_page: int | None = None,
        base_query=None,
    ) -> tuple[list[T], paginationMeta]:
        per_page = min(per_page or self._default_limit, self._max_limit)
        page = max(page, 1)
        offset = self.calculate_offset(page, per_page)

        if base_query is None:
            base_query = select(model)

        count_query = select(func.count()).select_from(base_query.subquery())
        total_result = await session.execute(count_query)
        total = total_result.scalar() or 0

        items_query = base_query.offset(offset).limit(per_page)
        items_result = await session.execute(items_query)
        items = list(items_result.scalars().all())

        total_pages = (total + per_page - 1) // per_page if per_page > 0 else 0
        has_next = page < total_pages
        has_prev = page > 1

        meta = paginationMeta(
            total=total,
            page=page,
            per_page=per_page,
            has_next=has_next,
            has_prev=has_prev,
        )

        return items, meta
