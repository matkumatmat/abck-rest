from __future__ import annotations

from typing import TYPE_CHECKING

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from components.enums.ErrorCodeEnum import errorCode
from components.logger.LoggerFactory import loggerFactory

if TYPE_CHECKING:
    from components.config.ComponentSettings import componentSettings


class csrfMiddleware(BaseHTTPMiddleware):

    SAFE_METHODS = {"GET", "HEAD", "OPTIONS", "TRACE"}

    def __init__(self, app, config: componentSettings) -> None:
        super().__init__(app)
        self._config = config
        self._enabled = config.csrf_enabled
        self._cookie_name = config.csrf_cookie_name
        self._header_name = config.csrf_header_name
        self._exempt_paths = set(config.csrf_exempt_paths)
        self._logger = loggerFactory.create("csrf")

    def _is_exempt(self, request: Request) -> bool:
        if request.method in self.SAFE_METHODS:
            return True
        return request.url.path in self._exempt_paths

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        if not self._enabled:
            return await call_next(request)

        if self._is_exempt(request):
            return await call_next(request)

        cookie_token = request.cookies.get(self._cookie_name)
        header_token = request.headers.get(self._header_name)

        if not cookie_token or not header_token:
            self._logger.warning(
                "csrf_missing",
                path=request.url.path,
                has_cookie=bool(cookie_token),
                has_header=bool(header_token),
            )
            return JSONResponse(
                status_code=403,
                content={
                    "code": errorCode.CSRF_INVALID.value,
                    "message": "CSRF token missing",
                },
            )

        if cookie_token != header_token:
            self._logger.warning("csrf_mismatch", path=request.url.path)
            return JSONResponse(
                status_code=403,
                content={
                    "code": errorCode.CSRF_INVALID.value,
                    "message": "CSRF token invalid",
                },
            )

        return await call_next(request)
