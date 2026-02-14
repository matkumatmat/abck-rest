from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any

from redis.asyncio import ConnectionPool, Redis

from components.database.RetryHandler import retryHandler
from components.exceptions.DatabaseException import cacheConnectionException, cacheKeyException
from components.logger.LoggingDatabase import loggingDatabase

if TYPE_CHECKING:
    from components.config.ComponentSettings import componentSettings


class redisEngine:

    def __init__(self, config: componentSettings) -> None:
        self._config = config
        self._pool: ConnectionPool | None = None
        self._client: Redis | None = None
        self._logger = loggingDatabase()
        self._retry = retryHandler(
            max_attempts=config.retry_max_attempts,
            base_delay=config.retry_base_delay,
            max_delay=config.retry_max_delay,
            backoff_factor=config.retry_backoff_factor,
        )

    async def connect(self) -> None:
        async def _connect() -> None:
            self._pool = ConnectionPool.from_url(
                self._config.redis_url,
                max_connections=self._config.redis_max_connections,
                decode_responses=self._config.redis_decode_responses,
            )
            self._client = Redis(connection_pool=self._pool)
            await self._client.ping()

        try:
            await self._retry.execute(_connect)
            self._logger.connection_success("Redis connected")
        except Exception as e:
            self._logger.connection_error(str(e))
            raise cacheConnectionException(f"Failed to connect to Redis: {e}")

    def _ensure_connected(self) -> Redis:
        if self._client is None:
            raise cacheConnectionException("Redis not connected. Call connect() first.")
        return self._client

    async def get(self, key: str) -> Any | None:
        client = self._ensure_connected()
        value = await client.get(key)
        if value is None:
            return None
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return value

    async def set(self, key: str, value: Any, ttl: int | None = None) -> bool:
        client = self._ensure_connected()
        ttl = ttl or self._config.redis_default_ttl
        serialized = json.dumps(value) if not isinstance(value, str) else value
        return await client.set(key, serialized, ex=ttl)

    async def get_raw(self, key: str) -> str | bytes | None:
        client = self._ensure_connected()
        return await client.get(key)

    async def set_raw(self, key: str, value: str | bytes, ttl: int | None = None) -> bool:
        client = self._ensure_connected()
        ttl = ttl or self._config.redis_default_ttl
        return await client.set(key, value, ex=ttl)

    async def delete(self, key: str) -> int:
        client = self._ensure_connected()
        return await client.delete(key)

    async def exists(self, key: str) -> bool:
        client = self._ensure_connected()
        return bool(await client.exists(key))

    async def expire(self, key: str, ttl: int) -> bool:
        client = self._ensure_connected()
        return await client.expire(key, ttl)

    async def ttl(self, key: str) -> int:
        client = self._ensure_connected()
        return await client.ttl(key)

    async def incr(self, key: str) -> int:
        client = self._ensure_connected()
        return await client.incr(key)

    async def keys(self, pattern: str) -> list[str]:
        client = self._ensure_connected()
        keys: list[str] = []
        cursor = 0
        while True:
            cursor, batch = await client.scan(cursor, match=pattern, count=100)
            keys.extend(batch)
            if cursor == 0:
                break
        return keys

    async def flush_pattern(self, pattern: str) -> int:
        client = self._ensure_connected()
        keys = await self.keys(pattern)
        if not keys:
            return 0
        return await client.delete(*keys)

    async def health(self) -> bool:
        if self._client is None:
            return False
        try:
            await self._client.ping()
            return True
        except Exception:
            return False

    async def close(self) -> None:
        if self._client is not None:
            await self._client.close()
            self._client = None
        if self._pool is not None:
            await self._pool.disconnect()
            self._pool = None
        self._logger.pool_event("disposed", "Redis connection closed")
