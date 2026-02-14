from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from components.crypto.CryptoFactory import cryptoFactory
    from components.database.PostgresEngine import postgresEngine
    from components.database.RedisEngine import redisEngine
    from components.email.EmailService import emailService
    from src.application.interfaces.UnitOfWorkInterface import unitOfWorkInterface
    from src.application.services.ApiKeyService import apiKeyService
    from src.application.services.AuthService import authService
    from src.application.services.SessionService import sessionService
    from src.application.services.TokenService import tokenService
    from src.application.services.VerificationService import verificationService
    from src.domain.config.Settings import settings

_settings: settings | None = None
_pg: postgresEngine | None = None
_redis: redisEngine | None = None
_crypto: cryptoFactory | None = None
_email: emailService | None = None

_uow: unitOfWorkInterface | None = None
_token_service: tokenService | None = None
_session_service: sessionService | None = None
_auth_service: authService | None = None
_verification_service: verificationService | None = None
_api_key_service: apiKeyService | None = None


def init_dependencies(
    config: settings,
    pg: postgresEngine,
    redis: redisEngine,
    crypto: cryptoFactory,
    email: emailService,
) -> None:
    global _settings, _pg, _redis, _crypto, _email

    _settings = config
    _pg = pg
    _redis = redis
    _crypto = crypto
    _email = email


def get_settings() -> settings:
    if _settings is None:
        raise RuntimeError("Dependencies not initialized")
    return _settings


def get_postgres() -> postgresEngine:
    if _pg is None:
        raise RuntimeError("Dependencies not initialized")
    return _pg


def get_redis() -> redisEngine:
    if _redis is None:
        raise RuntimeError("Dependencies not initialized")
    return _redis


def get_crypto() -> cryptoFactory:
    if _crypto is None:
        raise RuntimeError("Dependencies not initialized")
    return _crypto


def get_email() -> emailService:
    if _email is None:
        raise RuntimeError("Dependencies not initialized")
    return _email


def get_uow() -> unitOfWorkInterface:
    from src.infrastructure.postgres.PostgresUnitOfWork import postgresUnitOfWork

    pg = get_postgres()
    return postgresUnitOfWork(pg.session_factory)


def get_token_service() -> tokenService:
    global _token_service

    if _token_service is None:
        from src.application.services.TokenService import tokenService as _tokenServiceCls

        _token_service = _tokenServiceCls(
            config=get_settings(),
            uow=get_uow(),
            redis=get_redis(),
            crypto=get_crypto(),
        )

    return _token_service


def get_session_service() -> sessionService:
    global _session_service

    if _session_service is None:
        from src.application.services.SessionService import sessionService as _sessionServiceCls

        _session_service = _sessionServiceCls(
            config=get_settings(),
            uow=get_uow(),
            redis=get_redis(),
            token_service=get_token_service(),
        )

    return _session_service


def get_auth_service() -> authService:
    global _auth_service

    if _auth_service is None:
        from src.application.services.AuthService import authService as _authServiceCls

        _auth_service = _authServiceCls(
            config=get_settings(),
            uow=get_uow(),
            redis=get_redis(),
            crypto=get_crypto(),
            session_service=get_session_service(),
            token_service=get_token_service(),
            email_service=get_email(),
        )

    return _auth_service


def get_verification_service() -> verificationService:
    global _verification_service

    if _verification_service is None:
        from src.application.services.VerificationService import verificationService as _verificationServiceCls

        _verification_service = _verificationServiceCls(
            config=get_settings(),
            uow=get_uow(),
            crypto=get_crypto(),
            session_service=get_session_service(),
            token_service=get_token_service(),
            email_service=get_email(),
        )

    return _verification_service


def get_api_key_service() -> apiKeyService:
    global _api_key_service

    if _api_key_service is None:
        from src.application.services.ApiKeyService import apiKeyService as _apiKeyServiceCls

        _api_key_service = _apiKeyServiceCls(
            config=get_settings(),
            uow=get_uow(),
            crypto=get_crypto(),
        )

    return _api_key_service


def reset_services() -> None:
    global _token_service, _session_service, _auth_service, _verification_service, _api_key_service

    _token_service = None
    _session_service = None
    _auth_service = None
    _verification_service = None
    _api_key_service = None
