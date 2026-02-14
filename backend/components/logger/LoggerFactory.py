from __future__ import annotations

import logging
import sys
from typing import TYPE_CHECKING

import structlog
from structlog.contextvars import merge_contextvars

if TYPE_CHECKING:
    from structlog.stdlib import BoundLogger


def _configure_structlog(log_format: str = "json", log_level: str = "INFO") -> None:
    shared_processors: list = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.UnicodeDecoder(),
    ]

    if log_format == "json":
        renderer = structlog.processors.JSONRenderer()
    else:
        renderer = structlog.dev.ConsoleRenderer(colors=True)

    structlog.configure(
        processors=[
            *shared_processors,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        structlog.stdlib.ProcessorFormatter(
            processor=renderer,
            foreign_pre_chain=shared_processors,
        )
    )

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))


_configured = False


class loggerFactory:

    @staticmethod
    def create(
        name: str,
        level: str = "INFO",
        log_format: str = "json",
    ) -> BoundLogger:
        global _configured
        if not _configured:
            _configure_structlog(log_format, level)
            _configured = True

        return structlog.get_logger(name)

    @staticmethod
    def bind_context(**kwargs) -> None:
        structlog.contextvars.bind_contextvars(**kwargs)

    @staticmethod
    def clear_context() -> None:
        structlog.contextvars.clear_contextvars()

    @staticmethod
    def unbind_context(*keys: str) -> None:
        structlog.contextvars.unbind_contextvars(*keys)
