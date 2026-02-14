from __future__ import annotations

from typing import TYPE_CHECKING

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from components.enums.ErrorCodeEnum import errorCode
from components.logger.LoggerFactory import loggerFactory

if TYPE_CHECKING:
    from components.config.ComponentSettings import componentSettings
    from components.database.RedisEngine import redisEngine


class blacklistMiddleware(BaseHTTPMiddleware):

    def __init__(
        self,
        app,
        config: componentSettings,
        redis: redisEngine,
    ) -> None:
        super().__init__(app)
        self._config = config
        self._redis = redis
        self._logger = loggerFactory.create("blacklist")
        self._enabled = config.blacklist_enabled

    def _get_client_ip(self, request: Request) -> str:
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        if not self._enabled:
            return await call_next(request)

        client_ip = self._get_client_ip(request)

        try:
            is_blocked = await self._redis.exists(f"blacklist:ip:{client_ip}")
            if is_blocked:
                self._logger.warning("blocked_request", ip=client_ip, path=request.url.path)
                return JSONResponse(
                    status_code=403,
                    content={
                        "code": errorCode.FORBIDDEN.value,
                        "message": "Access denied",
                    },
                )
        except Exception as e:
            self._logger.error("blacklist_check_failed", error=str(e))

        return await call_next(request)
