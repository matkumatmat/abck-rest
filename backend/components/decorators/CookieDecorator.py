from __future__ import annotations

from functools import wraps
from typing import Callable

from fastapi import Request

from components.exceptions.BaseException import unauthorizedException
from components.logger.LoggingUserBehaviour import loggingUserBehaviour

_logger = loggingUserBehaviour()


def require_cookie(cookie_name: str) -> Callable:
    def decorator(func: Callable) -> Callable:
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

            cookie_value = request.cookies.get(cookie_name)
            if not cookie_value:
                _logger.security_event("missing_cookie", detail=cookie_name)
                raise unauthorizedException(f"Cookie '{cookie_name}' required")

            kwargs[cookie_name] = cookie_value
            return await func(*args, **kwargs)

        return wrapper
    return decorator
