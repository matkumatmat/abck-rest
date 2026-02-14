from __future__ import annotations

from collections.abc import Awaitable, Callable
from datetime import datetime
from typing import TYPE_CHECKING, Any, TypeVar

from sqlalchemy import delete

from components.logger.LoggerFactory import loggerFactory

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession
    from sqlmodel import SQLModel

T = TypeVar("T", bound="SQLModel")

_logger = loggerFactory.create("background_task")


class backgroundTaskFactory:

    @staticmethod
    async def cleanup(
        session: AsyncSession,
        model: type[T],
        expires_field: str,
        cutoff: datetime | None = None,
    ) -> int:
        cutoff = cutoff or datetime.utcnow()

        try:
            field = getattr(model, expires_field)
            stmt = delete(model).where(field < cutoff)
            result = await session.execute(stmt)
            await session.commit()
            deleted = result.rowcount or 0
            _logger.info(
                "cleanup_completed",
                model=model.__tablename__,
                deleted=deleted,
            )
            return deleted
        except Exception as e:
            await session.rollback()
            _logger.error("cleanup_failed", model=model.__tablename__, error=str(e))
            raise

    @staticmethod
    async def cleanup_used(
        session: AsyncSession,
        model: type[T],
        used_field: str = "used",
        expires_field: str = "expires_at",
        cutoff: datetime | None = None,
    ) -> int:
        cutoff = cutoff or datetime.utcnow()

        try:
            used = getattr(model, used_field)
            expires = getattr(model, expires_field)
            stmt = delete(model).where((used == True) | (expires < cutoff))
            result = await session.execute(stmt)
            await session.commit()
            deleted = result.rowcount or 0
            _logger.info(
                "cleanup_used_completed",
                model=model.__tablename__,
                deleted=deleted,
            )
            return deleted
        except Exception as e:
            await session.rollback()
            _logger.error("cleanup_used_failed", model=model.__tablename__, error=str(e))
            raise

    @staticmethod
    def wrap_async(
        coro_fn: Callable[..., Awaitable[Any]],
        *args,
        **kwargs,
    ) -> Callable[[], Awaitable[Any]]:
        async def wrapper() -> Any:
            try:
                return await coro_fn(*args, **kwargs)
            except Exception as e:
                _logger.error(
                    "background_task_failed",
                    function=coro_fn.__name__,
                    error=str(e),
                )
                raise

        return wrapper

    @staticmethod
    def create_cleanup_task(
        session_factory: Callable[[], AsyncSession],
        model: type[T],
        expires_field: str,
    ) -> Callable[[], Awaitable[int]]:
        async def task() -> int:
            async with session_factory() as session:
                return await backgroundTaskFactory.cleanup(session, model, expires_field)

        return task
