from __future__ import annotations

import time
from typing import TYPE_CHECKING

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from components.logger.LoggerFactory import loggerFactory

if TYPE_CHECKING:
    from components.config.ComponentSettings import componentSettings


class requestLogMiddleware(BaseHTTPMiddleware):

    def __init__(self, app, config: componentSettings) -> None:
        super().__init__(app)
        self._exclude_paths = set(config.request_log_exclude_paths)
        self._logger = loggerFactory.create("request")

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        if request.url.path in self._exclude_paths:
            return await call_next(request)

        start_time = time.perf_counter()

        response = await call_next(request)

        duration_ms = (time.perf_counter() - start_time) * 1000

        self._logger.info(
            "http_request",
            method=request.method,
            path=request.url.path,
            status=response.status_code,
            duration_ms=round(duration_ms, 2),
            client_ip=request.client.host if request.client else None,
        )

        return response
