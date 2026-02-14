from __future__ import annotations

from components.enums.ErrorCodeEnum import errorCode


class baseException(Exception):

    def __init__(
        self,
        message: str,
        code: errorCode = errorCode.INTERNAL_ERROR,
        status: int = 500,
        detail: dict | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.code = code
        self.status = status
        self.detail = detail or {}

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(message={self.message!r}, code={self.code.value}, status={self.status})"


class badRequestException(baseException):

    def __init__(self, message: str = "Bad request", detail: dict | None = None) -> None:
        super().__init__(
            message=message,
            code=errorCode.VALIDATION_ERROR,
            status=400,
            detail=detail,
        )


class validationException(baseException):

    def __init__(self, message: str, detail: dict | None = None) -> None:
        super().__init__(
            message=message,
            code=errorCode.VALIDATION_ERROR,
            status=422,
            detail=detail,
        )


class unauthorizedException(baseException):

    def __init__(self, message: str = "Unauthorized", detail: dict | None = None) -> None:
        super().__init__(
            message=message,
            code=errorCode.UNAUTHORIZED,
            status=401,
            detail=detail,
        )


class forbiddenException(baseException):

    def __init__(self, message: str = "Forbidden", detail: dict | None = None) -> None:
        super().__init__(
            message=message,
            code=errorCode.FORBIDDEN,
            status=403,
            detail=detail,
        )


class notFoundException(baseException):

    def __init__(self, message: str = "Not found", detail: dict | None = None) -> None:
        super().__init__(
            message=message,
            code=errorCode.NOT_FOUND,
            status=404,
            detail=detail,
        )


class alreadyExistsException(baseException):

    def __init__(self, message: str = "Already exists", detail: dict | None = None) -> None:
        super().__init__(
            message=message,
            code=errorCode.ALREADY_EXISTS,
            status=409,
            detail=detail,
        )


class rateLimitedException(baseException):

    def __init__(self, message: str = "Rate limit exceeded", detail: dict | None = None) -> None:
        super().__init__(
            message=message,
            code=errorCode.RATE_LIMITED,
            status=429,
            detail=detail,
        )


class serviceUnavailableException(baseException):

    def __init__(self, message: str = "Service unavailable", detail: dict | None = None) -> None:
        super().__init__(
            message=message,
            code=errorCode.SERVICE_UNAVAILABLE,
            status=503,
            detail=detail,
        )
