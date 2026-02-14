from __future__ import annotations

from typing import TYPE_CHECKING

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from components.logger.LoggerFactory import loggerFactory

if TYPE_CHECKING:
    from components.config.ComponentSettings import componentSettings
    from components.database.RedisEngine import redisEngine


class rateLimitWriter(BaseHTTPMiddleware):

    def __init__(
        self,
        app,
        config: componentSettings,
        redis: redisEngine,
    ) -> None:
        super().__init__(app)
        self._config = config
        self._redis = redis
        self._logger = loggerFactory.create("rate_limit")

    def _get_client_identifier(self, request: Request) -> str:
        user_id = getattr(request.state, "user_id", None)
        if user_id:
            return f"user:{user_id}"
        return f"ip:{request.client.host if request.client else 'unknown'}"

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        response = await call_next(request)

        if response.status_code < 400:
            try:
                identifier = self._get_client_identifier(request)
                endpoint = request.url.path
                key = f"rate_limit:{identifier}:{endpoint}"

                count = await self._redis.incr(key)
                if count == 1:
                    await self._redis.expire(key, self._config.rate_limit_window)

            except Exception as e:
                self._logger.warning("rate_limit_write_failed", error=str(e))

        return response
