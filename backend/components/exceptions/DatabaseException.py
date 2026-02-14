from __future__ import annotations

from components.enums.ErrorCodeEnum import errorCode
from components.exceptions.BaseException import baseException


class databaseConnectionException(baseException):

    def __init__(self, message: str = "Database connection failed", detail: dict | None = None) -> None:
        super().__init__(
            message=message,
            code=errorCode.DB_CONNECTION_FAILED,
            status=503,
            detail=detail,
        )


class databaseTimeoutException(baseException):

    def __init__(self, message: str = "Database operation timed out", detail: dict | None = None) -> None:
        super().__init__(
            message=message,
            code=errorCode.DB_TIMEOUT,
            status=504,
            detail=detail,
        )


class databaseIntegrityException(baseException):

    def __init__(self, message: str = "Database integrity error", detail: dict | None = None) -> None:
        super().__init__(
            message=message,
            code=errorCode.DB_INTEGRITY,
            status=409,
            detail=detail,
        )


class cacheConnectionException(baseException):

    def __init__(self, message: str = "Cache unavailable", detail: dict | None = None) -> None:
        super().__init__(
            message=message,
            code=errorCode.CACHE_UNAVAILABLE,
            status=503,
            detail=detail,
        )


class cacheKeyException(baseException):

    def __init__(self, message: str = "Cache key not found", detail: dict | None = None) -> None:
        super().__init__(
            message=message,
            code=errorCode.CACHE_KEY_ERROR,
            status=404,
            detail=detail,
        )


class circuitOpenException(baseException):

    def __init__(self, message: str = "Circuit breaker is open", detail: dict | None = None) -> None:
        super().__init__(
            message=message,
            code=errorCode.CIRCUIT_OPEN,
            status=503,
            detail=detail,
        )
