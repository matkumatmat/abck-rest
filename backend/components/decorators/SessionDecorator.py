from __future__ import annotations

from functools import wraps
from typing import Callable

from fastapi import Request

from components.exceptions.BaseException import unauthorizedException
from components.logger.LoggingUserBehaviour import loggingUserBehaviour

_logger = loggingUserBehaviour()


def require_session(cookie_name: str = "sid") -> Callable:
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

            session_id = request.cookies.get(cookie_name)
            if not session_id:
                _logger.security_event("missing_session_cookie", detail=cookie_name)
                raise unauthorizedException("Session cookie required")

            kwargs["session_id"] = session_id
            return await func(*args, **kwargs)

        return wrapper
    return decorator
