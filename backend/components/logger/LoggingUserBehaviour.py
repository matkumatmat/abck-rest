from __future__ import annotations

from typing import TYPE_CHECKING

from components.enums.LogCategoryEnum import logCategory
from components.logger.LoggerFactory import loggerFactory

if TYPE_CHECKING:
    from structlog.stdlib import BoundLogger


class loggingUserBehaviour:

    def __init__(self) -> None:
        self._logger: BoundLogger = loggerFactory.create("behavior")

    def _log(self, level: str, event: str, **kwargs) -> None:
        log_method = getattr(self._logger, level)
        log_method(
            event,
            category=logCategory.BEHAVIOR.value,
            **kwargs,
        )

    def action(self, user_id: str, action: str, detail: str | None = None, **kwargs) -> None:
        self._log("info", f"user.{action}", user_id=user_id, detail=detail, **kwargs)

    def auth_event(self, user_id: str, event: str, **kwargs) -> None:
        self._log("info", f"auth.{event}", user_id=user_id, **kwargs)

    def auth_failure(self, event: str, reason: str, **kwargs) -> None:
        self._log("warning", f"auth.{event}", reason=reason, **kwargs)

    def business_event(self, event: str, detail: str | None = None, **kwargs) -> None:
        self._log("info", f"business.{event}", detail=detail, **kwargs)

    def security_event(self, event: str, user_id: str | None = None, **kwargs) -> None:
        self._log("warning", f"security.{event}", user_id=user_id, **kwargs)
