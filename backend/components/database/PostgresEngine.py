from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import TYPE_CHECKING

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from components.database.RetryHandler import retryHandler
from components.exceptions.DatabaseException import databaseConnectionException
from components.logger.LoggingDatabase import loggingDatabase

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncEngine

    from components.config.ComponentSettings import componentSettings


class postgresEngine:

    def __init__(self, config: componentSettings) -> None:
        self._config = config
        self._engine: AsyncEngine | None = None
        self._session_factory: async_sessionmaker[AsyncSession] | None = None
        self._logger = loggingDatabase()
        self._retry = retryHandler(
            max_attempts=config.retry_max_attempts,
            base_delay=config.retry_base_delay,
            max_delay=config.retry_max_delay,
            backoff_factor=config.retry_backoff_factor,
        )

    async def create_engine(self) -> None:
        async def _create() -> None:
            self._engine = create_async_engine(
                self._config.database_url,
                pool_size=self._config.db_pool_size,
                max_overflow=self._config.db_max_overflow,
                pool_timeout=self._config.db_pool_timeout,
                pool_recycle=self._config.db_pool_recycle,
                echo=self._config.db_echo,
            )
            self._session_factory = async_sessionmaker(
                bind=self._engine,
                class_=AsyncSession,
                expire_on_commit=False,
                autoflush=False,
            )

        try:
            await self._retry.execute(_create)
            self._logger.connection_success("PostgreSQL engine created")
        except Exception as e:
            self._logger.connection_error(str(e))
            raise databaseConnectionException(f"Failed to create PostgreSQL engine: {e}")

    @asynccontextmanager
    async def session(self) -> AsyncGenerator[AsyncSession, None]:
        if self._session_factory is None:
            raise databaseConnectionException("Engine not initialized. Call create_engine() first.")

        session = self._session_factory()
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            self._logger.connection_error(f"Session error: {e}")
            raise
        finally:
            await session.close()

    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        if self._session_factory is None:
            raise databaseConnectionException("Engine not initialized. Call create_engine() first.")

        session = self._session_factory()
        try:
            yield session
        finally:
            await session.close()

    def pool_status(self) -> dict:
        if self._engine is None:
            return {"status": "not_initialized"}

        pool = self._engine.pool
        if isinstance(pool, NullPool):
            return {"status": "null_pool"}

        return {
            "status": "active",
            "size": pool.size(),
            "checked_in": pool.checkedin(),
            "checked_out": pool.checkedout(),
            "overflow": pool.overflow(),
        }

    @property
    def session_factory(self) -> async_sessionmaker[AsyncSession]:
        if self._session_factory is None:
            raise databaseConnectionException("Engine not initialized. Call create_engine() first.")
        return self._session_factory

    async def health(self) -> bool:
        if self._engine is None:
            return False
        try:
            async with self._engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
            return True
        except Exception:
            return False

    async def close(self) -> None:
        if self._engine is not None:
            await self._engine.dispose()
            self._engine = None
            self._session_factory = None
            self._logger.pool_event("disposed", "PostgreSQL engine closed")
