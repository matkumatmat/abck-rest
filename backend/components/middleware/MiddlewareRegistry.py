from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi.middleware.cors import CORSMiddleware

from components.middleware.CorrelationIdMiddleware import correlationIdMiddleware
from components.middleware.CsrfMiddleware import csrfMiddleware
from components.middleware.RequestLogMiddleware import requestLogMiddleware

if TYPE_CHECKING:
    from fastapi import FastAPI

    from components.config.ComponentSettings import componentSettings
    from components.database.RedisEngine import redisEngine


def register_middlewares(
    app: FastAPI,
    config: componentSettings,
    redis: redisEngine | None = None,
) -> None:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_middleware(correlationIdMiddleware)

    app.add_middleware(requestLogMiddleware, config=config)

    if config.csrf_enabled:
        app.add_middleware(csrfMiddleware, config=config)

    if redis is not None:
        from components.middleware.BlacklistMiddleware import blacklistMiddleware
        from components.middleware.RateLimitWriter import rateLimitWriter

        if config.blacklist_enabled:
            app.add_middleware(blacklistMiddleware, config=config, redis=redis)

        app.add_middleware(rateLimitWriter, config=config, redis=redis)
