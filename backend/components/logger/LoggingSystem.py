from __future__ import annotations

import os
import socket
from typing import TYPE_CHECKING

from components.enums.LogCategoryEnum import logCategory
from components.logger.LoggerFactory import loggerFactory

if TYPE_CHECKING:
    from structlog.stdlib import BoundLogger


class loggingSystem:

    def __init__(self, service_name: str) -> None:
        self._logger: BoundLogger = loggerFactory.create("system")
        self._service_name = service_name
        self._hostname = socket.gethostname()
        self._pid = os.getpid()

    def _log(self, level: str, event: str, **kwargs) -> None:
        log_method = getattr(self._logger, level)
        log_method(
            event,
            category=logCategory.SYSTEM.value,
            service_name=self._service_name,
            hostname=self._hostname,
            pid=self._pid,
            **kwargs,
        )

    def startup(self, detail: str) -> None:
        self._log("info", "startup", detail=detail)

    def shutdown(self, detail: str) -> None:
        self._log("info", "shutdown", detail=detail)

    def middleware_event(self, event: str, detail: str | None = None) -> None:
        self._log("info", f"middleware.{event}", detail=detail)

    def error(self, event: str, detail: str | None = None, **kwargs) -> None:
        self._log("error", event, detail=detail, **kwargs)

    def warning(self, event: str, detail: str | None = None, **kwargs) -> None:
        self._log("warning", event, detail=detail, **kwargs)

    def info(self, event: str, detail: str | None = None, **kwargs) -> None:
        self._log("info", event, detail=detail, **kwargs)

    def debug(self, event: str, detail: str | None = None, **kwargs) -> None:
        self._log("debug", event, detail=detail, **kwargs)
