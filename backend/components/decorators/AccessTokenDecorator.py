from __future__ import annotations

from functools import wraps
from typing import Annotated, Callable

from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from components.exceptions.BaseException import unauthorizedException
from components.logger.LoggingUserBehaviour import loggingUserBehaviour

_logger = loggingUserBehaviour()
bearer_scheme = HTTPBearer(auto_error=False)

BearerToken = Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)]


def require_access_token(func: Callable) -> Callable:
    @wraps(func)
    async def wrapper(*args, **kwargs):
        request: Request | None = kwargs.get("request")
        if request is None:
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break

        if request is None:
            raise unauthorizedException("Request not found")

        auth_header = request.headers.get("Authorization")
        if not auth_header:
            _logger.security_event("missing_auth_header")
            raise unauthorizedException("Authorization header required")

        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            _logger.security_event("invalid_auth_format", detail=auth_header[:20])
            raise unauthorizedException("Invalid authorization format. Expected: Bearer <token>")

        access_token = parts[1]
        kwargs["access_token"] = access_token
        return await func(*args, **kwargs)

    return wrapper
