from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING

from components.exceptions.BaseException import serviceUnavailableException

if TYPE_CHECKING:
    from components.logger.LoggingSystem import loggingSystem


class readinessGate:

    def __init__(
        self,
        checks: list[tuple[str, Callable[[], Awaitable[bool]]]] | None = None,
        logger: loggingSystem | None = None,
    ) -> None:
        self._checks: list[tuple[str, Callable[[], Awaitable[bool]]]] = checks or []
        self._logger = logger
        self._ready = False

    def register_check(self, name: str, check_fn: Callable[[], Awaitable[bool]]) -> None:
        self._checks.append((name, check_fn))

    async def wait_until_ready(
        self,
        timeout: int = 60,
        interval: int = 2,
    ) -> None:
        start_time = asyncio.get_event_loop().time()
        attempt = 0
        max_attempts = timeout // interval

        while True:
            attempt += 1
            elapsed = asyncio.get_event_loop().time() - start_time

            if elapsed >= timeout:
                failed = await self._get_failed_checks()
                error_msg = f"Startup timeout after {timeout}s. Failed checks: {failed}"
                if self._logger:
                    self._logger.error("readiness_timeout", detail=error_msg)
                raise serviceUnavailableException(error_msg)

            all_ready = True
            failed_checks: list[str] = []

            for name, check_fn in self._checks:
                try:
                    result = await check_fn()
                    if not result:
                        all_ready = False
                        failed_checks.append(name)
                except Exception as e:
                    all_ready = False
                    failed_checks.append(f"{name} ({e})")

            if all_ready:
                self._ready = True
                if self._logger:
                    self._logger.info("readiness_success", detail="All checks passed")
                return

            if self._logger:
                self._logger.info(
                    "readiness_waiting",
                    detail=f"Attempt {attempt}/{max_attempts}",
                    failed=failed_checks,
                )

            await asyncio.sleep(interval)

    async def _get_failed_checks(self) -> list[str]:
        failed: list[str] = []
        for name, check_fn in self._checks:
            try:
                result = await check_fn()
                if not result:
                    failed.append(name)
            except Exception as e:
                failed.append(f"{name} ({e})")
        return failed

    async def is_ready(self) -> bool:
        if self._ready:
            return True

        for name, check_fn in self._checks:
            try:
                result = await check_fn()
                if not result:
                    return False
            except Exception:
                return False

        self._ready = True
        return True

    @property
    def ready(self) -> bool:
        return self._ready
