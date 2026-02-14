from __future__ import annotations

import uuid

import structlog
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response


class correlationIdMiddleware(BaseHTTPMiddleware):

    HEADER_NAME = "X-Correlation-ID"

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        correlation_id = request.headers.get(self.HEADER_NAME) or str(uuid.uuid4())

        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(correlation_id=correlation_id)

        request.state.correlation_id = correlation_id

        response = await call_next(request)
        response.headers[self.HEADER_NAME] = correlation_id

        return response
