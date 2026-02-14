from __future__ import annotations

import traceback

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from components.enums.ErrorCodeEnum import errorCode
from components.exceptions.BaseException import baseException
from components.exceptions.ExceptionResponse import exceptionResponse
from components.logger.LoggerFactory import loggerFactory

_logger = loggerFactory.create("exception_handler")


def _create_response(code: str, message: str, status: int, detail: dict | None = None) -> JSONResponse:
    response = exceptionResponse.create(code=code, message=message, detail=detail)
    return JSONResponse(
        status_code=status,
        content=response.model_dump(by_alias=True, exclude_none=True),
    )


async def _base_exception_handler(request: Request, exc: baseException) -> JSONResponse:
    _logger.warning(
        "base_exception",
        code=exc.code.value,
        message=exc.message,
        status=exc.status,
        path=str(request.url.path),
    )
    return _create_response(
        code=exc.code.value,
        message=exc.message,
        status=exc.status,
        detail=exc.detail if exc.detail else None,
    )


async def _validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    errors = exc.errors()
    _logger.warning(
        "validation_error",
        path=str(request.url.path),
        errors=errors,
    )
    return _create_response(
        code=errorCode.VALIDATION_ERROR.value,
        message="Validation error",
        status=422,
        detail={"errors": errors},
    )


async def _http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    _logger.warning(
        "http_exception",
        status=exc.status_code,
        detail=exc.detail,
        path=str(request.url.path),
    )
    return _create_response(
        code=errorCode.INTERNAL_ERROR.value if exc.status_code >= 500 else errorCode.VALIDATION_ERROR.value,
        message=str(exc.detail) if exc.detail else "HTTP error",
        status=exc.status_code,
    )


async def _generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    tb = traceback.format_exc()
    _logger.error(
        "unhandled_exception",
        exception_type=type(exc).__name__,
        message=str(exc),
        traceback=tb,
        path=str(request.url.path),
    )
    return _create_response(
        code=errorCode.INTERNAL_ERROR.value,
        message="Internal server error",
        status=500,
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(baseException, _base_exception_handler)
    app.add_exception_handler(RequestValidationError, _validation_exception_handler)
    app.add_exception_handler(StarletteHTTPException, _http_exception_handler)
    app.add_exception_handler(Exception, _generic_exception_handler)
