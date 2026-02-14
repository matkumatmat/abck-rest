from __future__ import annotations

from typing import TYPE_CHECKING

from components.enums.LogCategoryEnum import logCategory
from components.logger.LoggerFactory import loggerFactory

if TYPE_CHECKING:
    from structlog.stdlib import BoundLogger


class loggingDatabase:

    def __init__(self, db_host: str = "", db_name: str = "") -> None:
        self._logger: BoundLogger = loggerFactory.create("database")
        self._db_host = db_host
        self._db_name = db_name

    def _log(self, level: str, event: str, **kwargs) -> None:
        log_method = getattr(self._logger, level)
        log_method(
            event,
            category=logCategory.DATABASE.value,
            db_host=self._db_host,
            db_name=self._db_name,
            **kwargs,
        )

    def query(self, sql: str, duration_ms: float, params_count: int = 0) -> None:
        self._log(
            "debug",
            "query.executed",
            sql=sql[:200],
            duration_ms=round(duration_ms, 2),
            params_count=params_count,
        )

    def slow_query(self, sql: str, duration_ms: float, threshold_ms: float) -> None:
        self._log(
            "warning",
            "query.slow",
            sql=sql[:200],
            duration_ms=round(duration_ms, 2),
            threshold_ms=threshold_ms,
        )

    def pool_event(self, event: str, detail: str | None = None, **kwargs) -> None:
        self._log("info", f"pool.{event}", detail=detail, **kwargs)

    def connection_error(self, error: str, **kwargs) -> None:
        self._log("error", "connection.error", error=error, **kwargs)

    def connection_success(self, detail: str | None = None) -> None:
        self._log("info", "connection.success", detail=detail)

    def migration(self, event: str, detail: str | None = None) -> None:
        self._log("info", f"migration.{event}", detail=detail)
