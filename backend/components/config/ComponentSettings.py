from __future__ import annotations

from pydantic_settings import BaseSettings


class componentSettings(BaseSettings):

    # -- PostgreSQL --
    database_url: str = "postgresql+asyncpg://user:pass@localhost:5432/db"
    db_pool_size: int = 10
    db_max_overflow: int = 20
    db_pool_timeout: int = 30
    db_pool_recycle: int = 3600
    db_echo: bool = False

    # -- Redis --
    redis_url: str = "redis://localhost:6379/0"
    redis_default_ttl: int = 3600
    redis_max_connections: int = 20
    redis_decode_responses: bool = True

    # -- Logger --
    log_level: str = "INFO"
    log_format: str = "json"

    # -- Crypto --
    crypto_master_key: str = ""
    crypto_default_hash: str = "argon2id"
    crypto_default_encrypt: str = "aes256gcm"
    crypto_argon_memory: int = 65536
    crypto_argon_iterations: int = 3
    crypto_argon_parallelism: int = 4

    # -- Health Check --
    health_check_urls: list[str] = []
    health_pg_latency_warn: int = 500
    health_pg_latency_critical: int = 2000
    health_redis_latency_warn: int = 100
    health_redis_latency_critical: int = 1000

    # -- Startup Readiness --
    startup_timeout: int = 60
    startup_check_interval: int = 2

    # -- HTTP Client --
    http_client_timeout: int = 30
    http_client_max_connections: int = 100
    http_client_retries: int = 0

    # -- Retry / Circuit Breaker --
    retry_max_attempts: int = 3
    retry_base_delay: float = 1.0
    retry_max_delay: float = 30.0
    retry_backoff_factor: float = 2.0
    circuit_failure_threshold: int = 5
    circuit_recovery_timeout: int = 60

    # -- Pagination --
    pagination_default_limit: int = 20
    pagination_max_limit: int = 100

    # -- Middleware: CORS --
    cors_origins: list[str] = ["http://localhost:3000"]

    # -- Middleware: Trusted Hosts --
    trusted_hosts: list[str] = ["*"]

    # -- Middleware: Rate Limit Writer --
    rate_limit_window: int = 60
    rate_limit_fallback_to_pg: bool = True

    # -- Middleware: Request Log --
    request_log_exclude_paths: list[str] = ["/health"]

    # -- Middleware: Blacklist --
    blacklist_enabled: bool = True

    # -- Middleware: CSRF --
    csrf_enabled: bool = True
    csrf_cookie_name: str = "_csrf"
    csrf_header_name: str = "X-CSRF-Token"
    csrf_exempt_paths: list[str] = ["/v1/auth/login", "/v1/auth/register", "/v1/token/refresh"]

    # -- Email (SMTP) --
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from_name: str = "No Reply"
    smtp_from_email: str = ""
    smtp_use_tls: bool = True
    email_retry_attempts: int = 3
    email_templates_dir: str = "components/email/templates"

    model_config = {"env_file": ".env", "extra": "ignore"}
