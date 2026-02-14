from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from components.crypto.CryptoFactory import cryptoFactory
from components.database.PostgresEngine import postgresEngine
from components.database.RedisEngine import redisEngine
from components.email.EmailService import emailService
from components.email.EmailTemplateEngine import emailTemplateEngine
from components.exceptions.ExceptionHandler import register_exception_handlers
from components.health.HealthCheck import healthCheck
from components.health.ReadinessGate import readinessGate
from components.http.HttpClientFactory import httpClientFactory
from components.logger.LoggerFactory import loggerFactory
from components.logger.LoggingSystem import loggingSystem
from components.middleware.MiddlewareRegistry import register_middlewares
from src.Dependencies import init_dependencies, reset_services
from src.domain.config.Settings import settings

config = settings()
logger = loggerFactory.create("main", level=config.log_level)
sys_log = loggingSystem(config.app_name)

pg = postgresEngine(config)
redis = redisEngine(config)
crypto = cryptoFactory(config)
http = httpClientFactory(config)
template_engine = emailTemplateEngine(config.email_templates_dir)
email = emailService(config, template_engine)
health = healthCheck(config, pg, redis, http)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    sys_log.startup("initializing auth-service engines")

    await pg.create_engine()
    await redis.connect()

    gate = readinessGate(
        [
            ("postgres", pg.health),
            ("redis", redis.health),
        ],
        logger=sys_log,
    )
    await gate.wait_until_ready(
        timeout=config.startup_timeout,
        interval=config.startup_check_interval,
    )

    init_dependencies(config, pg, redis, crypto, email)

    sys_log.startup("auth-service ready, accepting traffic")

    yield

    reset_services()
    await http.close()
    await pg.close()
    await redis.close()
    sys_log.shutdown("auth-service shutdown complete")


app = FastAPI(
    title=config.app_name,
    debug=config.debug,
    lifespan=lifespan,
)

register_exception_handlers(app)
register_middlewares(app, config)
app.include_router(health.router)

from src.infrastructure.routers.v1.AuthRouter import router as auth_router
from src.infrastructure.routers.v1.SessionRouter import router as session_router
from src.infrastructure.routers.v1.TokenRouter import router as token_router
from src.infrastructure.routers.v1.VerificationRouter import router as verification_router

app.include_router(auth_router)
app.include_router(session_router)
app.include_router(token_router)
app.include_router(verification_router)
