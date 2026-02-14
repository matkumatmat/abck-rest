from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from enum import Enum
from typing import TypeVar

from components.exceptions.DatabaseException import circuitOpenException
from components.logger.LoggerFactory import loggerFactory

T = TypeVar("T")


class circuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class retryHandler:

    def __init__(
        self,
        max_attempts: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 30.0,
        backoff_factor: float = 2.0,
    ) -> None:
        self._max_attempts = max_attempts
        self._base_delay = base_delay
        self._max_delay = max_delay
        self._backoff_factor = backoff_factor
        self._logger = loggerFactory.create("retry_handler")

    async def execute(
        self,
        fn: Callable[..., Awaitable[T]],
        *args,
        **kwargs,
    ) -> T:
        last_exception: Exception | None = None

        for attempt in range(1, self._max_attempts + 1):
            try:
                return await fn(*args, **kwargs)
            except Exception as e:
                last_exception = e
                if attempt < self._max_attempts:
                    delay = min(
                        self._base_delay * (self._backoff_factor ** (attempt - 1)),
                        self._max_delay,
                    )
                    self._logger.warning(
                        "retry_attempt",
                        attempt=attempt,
                        max_attempts=self._max_attempts,
                        delay=delay,
                        error=str(e),
                    )
                    await asyncio.sleep(delay)

        self._logger.error(
            "retry_exhausted",
            max_attempts=self._max_attempts,
            error=str(last_exception),
        )
        raise last_exception

    async def execute_with_fallback(
        self,
        primary_fn: Callable[..., Awaitable[T]],
        fallback_fn: Callable[..., Awaitable[T]],
        *args,
        **kwargs,
    ) -> T:
        try:
            return await self.execute(primary_fn, *args, **kwargs)
        except Exception as e:
            self._logger.warning(
                "fallback_triggered",
                primary_error=str(e),
            )
            return await fallback_fn(*args, **kwargs)


class circuitBreaker:

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
    ) -> None:
        self._failure_threshold = failure_threshold
        self._recovery_timeout = recovery_timeout
        self._state = circuitState.CLOSED
        self._failure_count = 0
        self._last_failure_time: float | None = None
        self._logger = loggerFactory.create("circuit_breaker")

    @property
    def state(self) -> circuitState:
        return self._state

    def _transition_to(self, new_state: circuitState) -> None:
        old_state = self._state
        self._state = new_state
        self._logger.info(
            "circuit_state_change",
            from_state=old_state.value,
            to_state=new_state.value,
        )

    async def call(
        self,
        fn: Callable[..., Awaitable[T]],
        *args,
        **kwargs,
    ) -> T:
        if self._state == circuitState.OPEN:
            if self._last_failure_time is not None:
                elapsed = asyncio.get_event_loop().time() - self._last_failure_time
                if elapsed >= self._recovery_timeout:
                    self._transition_to(circuitState.HALF_OPEN)
                else:
                    raise circuitOpenException(
                        f"Circuit is open, retry after {self._recovery_timeout - elapsed:.1f}s"
                    )

        try:
            result = await fn(*args, **kwargs)
            if self._state == circuitState.HALF_OPEN:
                self._transition_to(circuitState.CLOSED)
                self._failure_count = 0
            return result
        except Exception as e:
            self._failure_count += 1
            self._last_failure_time = asyncio.get_event_loop().time()

            if self._state == circuitState.HALF_OPEN:
                self._transition_to(circuitState.OPEN)
            elif self._failure_count >= self._failure_threshold:
                self._transition_to(circuitState.OPEN)

            raise e

    def reset(self) -> None:
        self._state = circuitState.CLOSED
        self._failure_count = 0
        self._last_failure_time = None
        self._logger.info("circuit_reset")
