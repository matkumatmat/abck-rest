# Project Plan: Reusable Components Library

> Target: Python >= 3.14 | FastAPI + DDD | SQLModel
> Packaging: `components/` folder di dalam tiap project (copy-paste)
> Semua components mengikuti aturan skill fastapi-ddd-backend

---

## Overview Arsitektur Components

```
components/
├── config/
│   ├── ComponentSettings.py       # centralized pydantic-settings untuk SEMUA components
│   └── env.example                # template .env untuk semua config components
├── enums/
│   ├── ErrorCodeEnum.py           # semua error code
│   ├── LogCategoryEnum.py         # SYSTEM, DATABASE, BEHAVIOR
│   ├── CryptoAlgorithmEnum.py     # hash, encrypt, signing algorithms
│   └── HealthStatusEnum.py        # HEALTHY, DEGRADED, UNHEALTHY
├── database/
│   ├── PostgresEngine.py          # async engine + connection pooling
│   ├── RedisEngine.py             # async redis + customizable TTL
│   └── RetryHandler.py            # retry + circuit breaker untuk DB/Redis reconnect
├── exceptions/
│   ├── BaseException.py           # base exception class
│   ├── DatabaseException.py       # PG + Redis specific exceptions
│   ├── ExceptionHandler.py        # FastAPI exception handler registry
│   └── ExceptionResponse.py       # standard error response schema
├── schemas/
│   ├── BaseResponse.py            # standard success response wrapper
│   └── PaginationSchema.py        # pagination metadata schema
├── pagination/
│   ├── CursorPagination.py        # cursor-based (feed, infinite scroll)
│   └── OffsetPagination.py        # offset-based (admin panel, static data)
├── health/
│   ├── HealthCheck.py             # PG, Redis, external API, system resources
│   └── ReadinessGate.py           # boot-time check, block traffic until ready
├── middleware/
│   ├── MiddlewareRegistry.py     # register semua middleware sekaligus (urutan benar)
│   ├── RequestLogMiddleware.py    # request/response logging
│   ├── CorrelationIdMiddleware.py # request ID tracking (X-Correlation-ID)
│   ├── RateLimitWriter.py         # tulis rate limit data ke Redis/PG
│   ├── TrustedHostMiddleware.py   # IP whitelist
│   ├── BlacklistMiddleware.py     # IP/token/user blacklist blocker
│   └── CsrfMiddleware.py         # CSRF protection untuk session-based auth
├── http/
│   └── HttpClientFactory.py       # async HTTP client (inter-service, external API)
├── decorators/
│   ├── SessionDecorator.py        # require session cookie
│   ├── AccessTokenDecorator.py    # require Bearer token
│   └── CookieDecorator.py         # require custom cookie
├── crypto/
│   └── CryptoFactory.py          # Python wrapper untuk Rust binary (.whl)
├── email/
│   ├── EmailService.py            # async SMTP sender (Gmail)
│   ├── EmailTemplateEngine.py     # MJML loader + render dengan variable injection
│   └── templates/                 # .mjml template files
│       ├── EmailVerification.mjml
│       ├── PasswordReset.mjml
│       └── Welcome.mjml
├── logger/
│   ├── LoggerFactory.py           # structlog JSON factory
│   ├── LoggingSystem.py           # system lifecycle logs
│   ├── LoggingDatabase.py         # query, pool, connection logs
│   └── LoggingUserBehaviour.py    # user action, audit trail
├── uuid/
│   └── UuidGenerator.py           # UUID7 generator
└── tasks/
    └── BackgroundTaskFactory.py   # reusable cleanup/scheduled tasks
```

---

## Component #0: Centralized Config

**Files**: `components/config/ComponentSettings.py` + `components/config/env.example`

**Responsibility**: Satu source of truth untuk SEMUA config components. Project-level `Settings.py` cukup inherit dari sini, ga perlu urus dotenv atau path manual.

**Key Design**:
- Class `componentSettings(BaseSettings)` — pydantic-settings, semua config components ada disini
- Project-level `Settings.py` tinggal inherit dan extend:
  ```python
  from components.config.ComponentSettings import componentSettings

  class settings(componentSettings):
      # project-specific config tambahan
      app_name: str = "my-service"
      app_port: int = 8000
  ```
- `model_config` di `componentSettings` set `env_file = ".env"` dan `extra = "ignore"`
- Dengan `extra = "ignore"`, project bisa punya ENV vars tambahan tanpa error
- TIDAK pakai `python-dotenv` langsung — pydantic-settings handle `.env` loading sendiri

### ComponentSettings.py — Full Config Map

```python
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
```

### env.example

```env
# ============================================
# COMPONENTS CONFIG
# ============================================

# -- PostgreSQL --
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/dbname
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=20
DB_POOL_TIMEOUT=30
DB_POOL_RECYCLE=3600
DB_ECHO=false

# -- Redis --
REDIS_URL=redis://localhost:6379/0
REDIS_DEFAULT_TTL=3600
REDIS_MAX_CONNECTIONS=20
REDIS_DECODE_RESPONSES=true

# -- Logger --
LOG_LEVEL=INFO
LOG_FORMAT=json

# -- Crypto (Rust) --
CRYPTO_DEFAULT_HASH=argon2id
CRYPTO_DEFAULT_ENCRYPT=aes256gcm
CRYPTO_ARGON_MEMORY=65536
CRYPTO_ARGON_ITERATIONS=3
CRYPTO_ARGON_PARALLELISM=4

# -- Health Check --
HEALTH_CHECK_URLS=["https://api.external.com/ping"]
HEALTH_PG_LATENCY_WARN=500
HEALTH_PG_LATENCY_CRITICAL=2000
HEALTH_REDIS_LATENCY_WARN=100
HEALTH_REDIS_LATENCY_CRITICAL=1000

# -- Startup Readiness --
STARTUP_TIMEOUT=60
STARTUP_CHECK_INTERVAL=2

# -- HTTP Client --
HTTP_CLIENT_TIMEOUT=30
HTTP_CLIENT_MAX_CONNECTIONS=100
HTTP_CLIENT_RETRIES=0

# -- Retry / Circuit Breaker --
RETRY_MAX_ATTEMPTS=3
RETRY_BASE_DELAY=1.0
RETRY_MAX_DELAY=30.0
RETRY_BACKOFF_FACTOR=2.0
CIRCUIT_FAILURE_THRESHOLD=5
CIRCUIT_RECOVERY_TIMEOUT=60

# -- Pagination --
PAGINATION_DEFAULT_LIMIT=20
PAGINATION_MAX_LIMIT=100

# -- Middleware: CORS --
CORS_ORIGINS=["http://localhost:3000"]

# -- Middleware: Trusted Hosts --
TRUSTED_HOSTS=["*"]

# -- Middleware: Rate Limit --
RATE_LIMIT_WINDOW=60
RATE_LIMIT_FALLBACK_TO_PG=true

# -- Middleware: Request Log --
REQUEST_LOG_EXCLUDE_PATHS=["/health"]

# -- Middleware: Blacklist --
BLACKLIST_ENABLED=true

# -- Middleware: CSRF --
CSRF_ENABLED=true
CSRF_COOKIE_NAME=_csrf
CSRF_HEADER_NAME=X-CSRF-Token
CSRF_EXEMPT_PATHS=["/v1/auth/login","/v1/auth/register","/v1/token/refresh"]

# -- Email (SMTP) --
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_NAME=No Reply
SMTP_FROM_EMAIL=your-email@gmail.com
SMTP_USE_TLS=true
EMAIL_RETRY_ATTEMPTS=3
EMAIL_TEMPLATES_DIR=components/email/templates

# ============================================
# PROJECT-SPECIFIC CONFIG (extend di Settings.py)
# ============================================
# APP_NAME=my-service
# APP_PORT=8000
# DEBUG=false
```

### Cara Pakai di Project

**Project Settings.py** (`src/domain/config/Settings.py`):

```python
from components.config.ComponentSettings import componentSettings

class settings(componentSettings):
    app_name: str = "auth-service"
    app_port: int = 8002
    debug: bool = False
    # ... project-specific fields
```

**Di mana saja butuh config**:

```python
from src.domain.config.Settings import settings

config = settings()  # auto-load dari .env, semua components config included
```

Satu `config` object, semua components langsung terima config yang sama. Ga perlu parse `.env` manual di mana-mana.

---

## Component Enums: Shared Enums

**Files**: 4 file dalam `components/enums/`

**Responsibility**: Semua enum yang dipakai lintas components. Centralized supaya ga ada duplikasi enum di masing-masing component.

### ErrorCodeEnum.py
```python
from enum import Enum

class errorCode(Enum):
    DB_CONNECTION_FAILED = "DB_CONNECTION_FAILED"
    DB_TIMEOUT = "DB_TIMEOUT"
    DB_INTEGRITY = "DB_INTEGRITY"
    CACHE_UNAVAILABLE = "CACHE_UNAVAILABLE"
    CACHE_KEY_ERROR = "CACHE_KEY_ERROR"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"
    NOT_FOUND = "NOT_FOUND"
    ALREADY_EXISTS = "ALREADY_EXISTS"
    RATE_LIMITED = "RATE_LIMITED"
    BLACKLISTED = "BLACKLISTED"
    CSRF_INVALID = "CSRF_INVALID"
    INTERNAL_ERROR = "INTERNAL_ERROR"
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"
    CIRCUIT_OPEN = "CIRCUIT_OPEN"
```

### LogCategoryEnum.py
```python
from enum import Enum

class logCategory(Enum):
    SYSTEM = "system"
    DATABASE = "database"
    BEHAVIOR = "behavior"
```

### CryptoAlgorithmEnum.py
```python
from enum import Enum

class hashAlgorithm(Enum):
    ARGON2ID = "argon2id"
    BLAKE3 = "blake3"
    SHA3_256 = "sha3_256"

class encryptAlgorithm(Enum):
    AES256GCM = "aes256gcm"
    CHACHA20_POLY1305 = "chacha20poly1305"

class signAlgorithm(Enum):
    HMAC_SHA256 = "hmac_sha256"
    ED25519 = "ed25519"
```

### HealthStatusEnum.py
```python
from enum import Enum

class healthStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
```

Semua enum mengikuti convention: camelCase class, UPPER_SNAKE member. Project bisa extend enum ini kalau perlu tambahan value spesifik.

---

## Component #1: PostgreSQL Engine

**File**: `components/database/PostgresEngine.py`

**Responsibility**: Async PostgreSQL engine dengan connection pooling, session management, dan pool health monitoring.

**Key Design**:
- Class `postgresEngine` — bukan factory karena ini singleton engine per-app
- Constructor terima config (url, pool_size, max_overflow, pool_timeout, pool_recycle)
- Semua config dari ENV via pydantic-settings, TIDAK hardcode
- Method `create_engine()` — inisialisasi async engine + session factory
- Method `session()` — async context manager, auto commit/rollback
- Method `raw_connection()` — untuk kasus perlu raw asyncpg connection (bulk insert, COPY, dll)
- Method `pool_status()` — return dict pool metrics (size, checked_in, checked_out, overflow)
- Method `close()` — dispose engine gracefully
- Semua error di-log via logger component, TIDAK silent

**Config yang diekspose**:

| Config | Type | Default | Deskripsi |
|--------|------|---------|-----------|
| `database_url` | `str` | required | PostgreSQL async URL |
| `db_pool_size` | `int` | `10` | Base pool size |
| `db_max_overflow` | `int` | `20` | Extra connections saat pool penuh |
| `db_pool_timeout` | `int` | `30` | Detik tunggu sebelum timeout |
| `db_pool_recycle` | `int` | `3600` | Detik sebelum recycle connection |
| `db_echo` | `bool` | `False` | Log SQL queries |

**Dependency**: SQLAlchemy asyncio, asyncpg, logger component

---

## Component #2: Redis Engine

**File**: `components/database/RedisEngine.py`

**Responsibility**: Async Redis client dengan customizable TTL, connection management, dan convenience methods.

**Key Design**:
- Class `redisEngine`
- Default TTL configurable via ENV, tapi bisa di-override per-call
- Method `connect()` / `close()` — lifecycle
- Method `get(key)` / `set(key, value, ttl=None)` / `delete(key)` — basic ops, auto JSON serialize/deserialize
- Method `get_raw(key)` / `set_raw(key, value, ttl=None)` — tanpa serialization, untuk binary/string data
- Method `exists(key)` — check key existence
- Method `expire(key, ttl)` — update TTL existing key
- Method `keys(pattern)` — scan keys by pattern (pakai SCAN, bukan KEYS)
- Method `flush_pattern(pattern)` — delete semua keys yang match pattern (pakai pipeline + SCAN)
- Method `health()` — PING check
- Semua error di-log, TIDAK silent

**Config yang diekspose**:

| Config | Type | Default | Deskripsi |
|--------|------|---------|-----------|
| `redis_url` | `str` | required | Redis connection URL |
| `redis_default_ttl` | `int` | `3600` | Default TTL (detik) |
| `redis_max_connections` | `int` | `20` | Max pool connections |
| `redis_decode_responses` | `bool` | `True` | Auto decode |

**Dependency**: redis.asyncio, logger component

---

## Component #3: Exceptions

**Files**: 4 file dalam `components/exceptions/`

### 3a. BaseException.py
- Class `baseException(Exception)` — field: `message`, `code` (enum), `status` (HTTP status int)
- Semua exception turunan dari sini

### 3b. DatabaseException.py
- `databaseConnectionException` — gagal connect PG/Redis
- `databaseTimeoutException` — query timeout
- `databaseIntegrityException` — unique constraint, FK violation
- `cacheConnectionException` — Redis unavailable
- `cacheKeyException` — key not found / expired
- Semua inherit dari `baseException` dengan code dari enum

### 3c. ExceptionHandler.py
- Function `register_exception_handlers(app: FastAPI)` — register semua handler sekaligus
- Handler untuk: `baseException`, `RequestValidationError`, `HTTPException`, `Exception` (catch-all)
- Setiap handler return format consistent dari `ExceptionResponse`
- Catch-all WAJIB log error detail (str(e), type(e).__name__, traceback)

### 3d. ExceptionResponse.py
- Pydantic schema `exceptionResponse` — field: `success` (always False), `_c` (code, obfuscated), `_m` (message, obfuscated), `_ts` (timestamp)
- Semua error response consistent format ini

**Error Code Enum**: Sudah di-maintain di `components/enums/ErrorCodeEnum.py` (lihat Component Enums). Exception classes import dari sana.

---

## Component #4: Health Check

**File**: `components/health/HealthCheck.py`

**Responsibility**: Comprehensive health check — database, cache, external API, system resources.

**Key Design**:
- Class `healthCheck`
- Constructor terima: `postgresEngine`, `redisEngine`, list of external URLs (configurable)
- Method `check_all()` — jalankan semua check, return aggregated result
- Method `check_postgres()` — SELECT 1, return latency ms
- Method `check_redis()` — PING, return latency ms
- Method `check_external(url)` — HTTP HEAD request, return status + latency
- Method `check_system()` — disk usage %, memory usage %, CPU % (pakai `psutil`)
- Response schema `healthResponse`:
  - `status`: `"healthy"` | `"degraded"` | `"unhealthy"` (enum)
  - `checks`: dict per-component dengan `status`, `latency_ms`, `detail`
  - `_ts`: timestamp
- Threshold configurable: misal PG latency > 500ms = degraded, > 2000ms = unhealthy
- Register sebagai router endpoint: `GET /health` (public) dan `GET /health/detail` (internal only)

**Dependency**: psutil, aiohttp (untuk external check), database components, logger

---

## Component #5: Middleware

**Files**: 5 file dalam `components/middleware/`

### 5a. RequestLogMiddleware.py
- Log setiap request: method, path, status_code, duration_ms, client IP
- Log setiap response: status_code, content_length
- Pakai `LoggingSystem` untuk log
- Exclude configurable paths (misal `/health` ga perlu di-log)

### 5b. CorrelationIdMiddleware.py
- Generate UUID7 sebagai `X-Correlation-ID` kalau belum ada di request header
- Inject ke `structlog.contextvars` supaya semua log dalam 1 request punya ID yang sama
- Append ke response header juga

### 5c. RateLimitWriter.py
- BUKAN enforcer — hanya TULIS data rate limit ke Redis
- Data: `{client_ip}:{endpoint}:{window}` -> counter
- Increment counter per request, set TTL = window duration
- Fallback ke PostgreSQL kalau Redis down
- Config: window_seconds, configurable per-route atau global

### 5d. TrustedHostMiddleware.py
- Whitelist IP addresses / CIDR ranges dari ENV
- Kalau request dari IP di luar whitelist -> return 403
- Config: `trusted_hosts: list[str]` dari ENV
- Support wildcard `*` untuk disable (development mode)

### 5e. BlacklistMiddleware.py
- Check request terhadap blacklist: IP, token, user_id
- Blacklist data di Redis (set data structure)
- Method `add_to_blacklist(type, value, ttl)` / `remove_from_blacklist(type, value)`
- Kalau match blacklist -> return 403 dengan code `BLACKLISTED`
- Log blocked attempt via `LoggingSystem`

### 5f. CsrfMiddleware.py
- CSRF protection khusus untuk session-based auth (cookie)
- JWT via Authorization header TIDAK perlu CSRF karena browser ga auto-attach
- Flow:
  - Login response set CSRF token di cookie (`csrf_token`, HttpOnly=False supaya JS bisa baca)
  - Setiap state-changing request (POST/PUT/DELETE) WAJIB kirim CSRF token di header `X-CSRF-Token`
  - Middleware compare: header `X-CSRF-Token` == cookie `csrf_token`
  - Mismatch -> reject 403 dengan code `CSRF_INVALID`
- CSRF token di-generate per-session (bukan per-request) — avoid complexity, cukup aman
- Token: random string via `uuidGenerator` atau `cryptoFactory.hash_data(session_id + secret)`
- Config:
  - `csrf_enabled: bool = True` — bisa disable untuk development
  - `csrf_cookie_name: str = "_csrf"`
  - `csrf_header_name: str = "X-CSRF-Token"`
  - `csrf_exempt_paths: list[str] = ["/v1/auth/login", "/v1/auth/register", "/v1/token/refresh"]` — paths yang ga perlu CSRF
- Safe methods (GET, HEAD, OPTIONS) di-skip otomatis

**Registration**: Function `register_middlewares(app, config)` yang register semua middleware sekaligus dengan urutan yang benar.

---

## Component #6: Crypto Factory (Rust)

**File**: `components/crypto/CryptoFactory.py` (Python wrapper)

**Rust Crate**: Separate repo, build sekali jadi `.whl`, distribute via:
- Option A: Private PyPI (recommended untuk tim)
- Option B: `.whl` file di shared storage, `pip install ./path/to/wheel.whl`
- Option C: Git release artifact, `pip install https://.../*.whl`

**Build Strategy**:
- Maturin build dengan `--release` flag
- Target multiple platform: `manylinux_2_28_x86_64`, `macosx_arm64` (sesuai deploy target)
- Hasil build = `.whl` file yang sudah compiled, TIDAK perlu Rust toolchain saat install
- CI/CD: GitHub Actions build wheel per-platform, upload sebagai release artifact

**Python Wrapper Design** (class `cryptoFactory`):
- Import dari installed Rust package: `from nama_crate import ...`
- Method `hash_password(plain, algorithm=None)` — default Argon2id, configurable
- Method `verify_password(plain, hashed)` — auto-detect algorithm dari hash prefix
- Method `hash_data(data, algorithm=None)` — generic hashing (BLAKE3, SHA3, custom)
- Method `encrypt(plaintext, key, algorithm=None)` — AES-256-GCM default, ChaCha20-Poly1305 option
- Method `decrypt(ciphertext, key, algorithm=None)` — auto-detect dari metadata
- Method `sign(payload, secret, algorithm=None)` — HMAC-SHA256, Ed25519
- Method `verify_signature(payload, signature, secret)` — verify
- Method `generate_token(payload, secret, expires_in)` — JWT-like token (bisa custom format)
- Method `decode_token(token, secret)` — decode + verify expiry
- Semua algorithm configurable via enum `cryptoAlgorithmEnum`
- Custom algorithm: user bisa register custom hash/encrypt function di Rust side

**Rust Crate Structure** (high-level):
```
crypto_crate/
├── src/
│   ├── lib.rs          # PyO3 module entry
│   ├── hashing.rs      # Argon2id, BLAKE3, SHA3, custom
│   ├── encryption.rs   # AES-256-GCM, ChaCha20-Poly1305
│   ├── signing.rs      # HMAC, Ed25519, JWT
│   └── config.rs       # algorithm enum, configurable params
├── Cargo.toml
└── pyproject.toml       # maturin config
```

**Config di Python side**:

| Config | Type | Default | Deskripsi |
|--------|------|---------|-----------|
| `crypto_default_hash` | `str` | `"argon2id"` | Default hash algorithm |
| `crypto_default_encrypt` | `str` | `"aes256gcm"` | Default encryption |
| `crypto_argon_memory` | `int` | `65536` | Argon2 memory cost (KB) |
| `crypto_argon_iterations` | `int` | `3` | Argon2 time cost |
| `crypto_argon_parallelism` | `int` | `4` | Argon2 parallelism |

---

## Component #7: Logging Factory

**Files**: 4 file dalam `components/logger/`

### 7a. LoggerFactory.py
- Class `loggerFactory` — structlog JSON output
- Method `create(name, category)` -> return bound logger dengan category context
- Structlog config: JSON renderer, ISO timestamp, log level, contextvars (untuk correlation ID)
- Log level configurable via ENV

### 7b. LoggingSystem.py
- Class `loggingSystem` — pre-configured logger dengan category `SYSTEM`
- Use case: app startup, shutdown, middleware events, health check, internal errors
- Method: `startup(detail)`, `shutdown(detail)`, `middleware_event(event, detail)`, `error(event, detail)`
- Auto-bind: `service_name`, `hostname`, `pid`

### 7c. LoggingDatabase.py
- Class `loggingDatabase` — pre-configured logger dengan category `DATABASE`
- Use case: query execution, slow query warning, connection pool events, migration
- Method: `query(sql, duration_ms, params_count)`, `slow_query(sql, duration_ms, threshold)`, `pool_event(event, detail)`, `connection_error(error)`
- Auto-bind: `db_host`, `db_name`

### 7d. LoggingUserBehaviour.py
- Class `loggingUserBehaviour` — pre-configured logger dengan category `BEHAVIOR`
- Use case: user login, logout, action audit, business events
- Method: `action(user_id, action, detail)`, `auth_event(user_id, event)`, `business_event(event, detail)`
- Auto-bind: `correlation_id` (dari contextvars)

**Semua logger output JSON** ke stdout. Format:

```json
{
  "timestamp": "2026-02-12T10:30:00Z",
  "level": "info",
  "event": "user_login",
  "category": "behavior",
  "correlation_id": "019abc...",
  "user_id": "usr_123",
  "service_name": "auth-service"
}
```

---

## Component #8: UUID Generator

**File**: `components/uuid/UuidGenerator.py`

**Key Design**:
- Class `uuidGenerator`
- Method `create()` -> `str` — UUID7 (time-ordered, sortable)
- Method `create_hex()` -> `str` — UUID7 tanpa dash
- Method `create_bytes()` -> `bytes` — raw 16 bytes
- Method `create_prefixed(prefix)` -> `str` — misal `usr_019abc...`, `ses_019abc...`
- Method `is_valid(value)` -> `bool` — validate UUID format
- Method `extract_timestamp(uuid7_str)` -> `datetime` — extract waktu dari UUID7
- Pakai `uuid6` library (atau `uuid_utils` yang Rust-backed untuk performance)

**Kenapa UUID7**:
- Time-ordered = index-friendly di PostgreSQL (B-tree friendly, no page splits)
- Sortable by creation time tanpa perlu kolom `created_at` tambahan untuk sorting
- Lebih aman dari UUID4 (tidak bisa di-brute-force urutannya)

---

## Component #9: Background Task Factory

**File**: `components/tasks/BackgroundTaskFactory.py`

**Responsibility**: Reusable background task registry. Define task sekali, trigger dari mana saja.

**Key Design**:
- Class `backgroundTaskFactory`
- Constructor terima: logger, database engine, redis engine (optional deps)
- Method `cleanup(model_class, filter_column, threshold, batch_size=1000)`:
  - Generic cleanup — hapus rows dimana `filter_column < threshold`
  - Pakai batch delete (LIMIT + loop) supaya ga lock table lama
  - Log jumlah deleted rows
  - Contoh: `cleanup(sessionModel, "expires_at", datetime.utcnow())`
- Method `expire_keys(pattern, dry_run=False)`:
  - Redis key cleanup by pattern
  - `dry_run=True` hanya log tanpa delete
- Method `execute(task_fn, *args, **kwargs)`:
  - Generic executor — jalankan callable apapun sebagai background task
  - Wrap dengan try/except + logging
  - Contoh: `execute(send_email, to="x@y.com", subject="Welcome")`
- Method `schedule(task_fn, *args, **kwargs)`:
  - Return callable yang bisa langsung di-pass ke FastAPI `BackgroundTasks.add_task()`

**Pola Penggunaan di Router**:

```python
@router.post("/auth/logout")
async def logout(bg: BackgroundTasks, ...):
    # ... logout logic
    bg.add_task(
        task_factory.cleanup,
        model_class=sessionModel,
        filter_column="expires_at",
        threshold=datetime.utcnow(),
    )
    bg.add_task(
        task_factory.execute,
        notify_audit_log,
        user_id=user.id,
        action="logout",
    )
```

**Tidak hardcode**: task_fn, model_class, filter_column, threshold semua sebagai parameter. Bisa pakai untuk cleanup apa saja tanpa bikin function baru.

---

## Component #10: HTTP Client Factory

**File**: `components/http/HttpClientFactory.py`

**Responsibility**: Async HTTP client yang reusable untuk inter-service communication dan external API calls. Satu session, connection pooling, timeout configurable.

**Key Design**:
- Class `httpClientFactory`
- Constructor terima: config (base_url optional, timeout, max_connections), logger
- Internal: satu `aiohttp.ClientSession` yang di-reuse (bukan create per-request)
- Method `get(url, headers=None, params=None)` -> dict/bytes
- Method `post(url, data=None, json=None, headers=None)` -> dict/bytes
- Method `put(url, data=None, json=None, headers=None)` -> dict/bytes
- Method `delete(url, headers=None)` -> dict/bytes
- Method `head(url, headers=None)` -> response status + headers (untuk health check external)
- Method `request(method, url, **kwargs)` -> generic, semua method di atas shortcut ke sini
- Auto-inject `X-Correlation-ID` dari contextvars ke setiap outgoing request
- Auto-inject `X-Service-Name` dari config
- Response handling: auto-parse JSON jika content-type JSON, otherwise return raw bytes
- Error handling: wrap `aiohttp` exceptions jadi `baseException` dengan code yang jelas
- Timeout per-request bisa override default
- Method `close()` — cleanup session

**Config**:

| Config | Type | Default | Deskripsi |
|--------|------|---------|-----------|
| `http_client_timeout` | `int` | `30` | Default timeout (detik) |
| `http_client_max_connections` | `int` | `100` | Max connection pool |
| `http_client_retries` | `int` | `0` | Auto-retry count (0 = no retry) |

**Use Case**:
- Health check external API: `await http.head("https://api.external.com/ping")`
- Inter-service ke central auth: `await http.get(f"{central_url}/users/{user_id}")`
- Third-party webhook: `await http.post(webhook_url, json=payload)`

---

## Component #11: Base Response Schema

**Files**: `components/schemas/BaseResponse.py` + `components/schemas/PaginationSchema.py`

**Responsibility**: Standardisasi format response di SEMUA project. Success dan error punya wrapper yang consistent.

### 11a. BaseResponse.py

```python
from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel
from typing import Any

class baseResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        alias_generator=to_camel,
    )

class baseRequest(BaseModel):
    model_config = ConfigDict(strict=True)

class successResponse(BaseModel):
    success: bool = True
    data: Any = None
    meta: dict | None = None

    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=to_camel,
    )
```

**Pola Penggunaan**:
- Semua response schema project inherit dari `baseResponse`
- Semua request schema project inherit dari `baseRequest`
- Router return dibalut `successResponse`:
  ```python
  return successResponse(data=user_response, meta={"page": 1})
  ```
- Error return `exceptionResponse` (dari Component #3)
- Client selalu terima format: `{"success": true/false, "data": ..., "meta": ...}` atau `{"success": false, "_c": ..., "_m": ..., "_ts": ...}`

### 11b. PaginationSchema.py

```python
class paginationMeta(BaseModel):
    total: int
    page: int | None = None
    per_page: int | None = None
    cursor: str | None = None
    has_next: bool = False
    has_prev: bool = False

    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=to_camel,
    )
```

Dipakai sebagai `meta` di `successResponse`:
```python
return successResponse(
    data=items,
    meta=paginationMeta(total=100, page=1, per_page=20, has_next=True).model_dump(by_alias=True),
)
```

---

## Component #12: Pagination Components

**Files**: `components/pagination/CursorPagination.py` + `components/pagination/OffsetPagination.py`

**Responsibility**: Reusable pagination logic. Bisa diterapkan ke SQLModel query apapun tanpa tulis ulang.

### 12a. CursorPagination.py

- Class `cursorPagination`
- Method `paginate(query, cursor=None, limit=20, order_column="id")`:
  - Decode cursor (base64 encoded last-seen value)
  - Apply WHERE clause: `WHERE order_column > decoded_cursor`
  - Fetch `limit + 1` rows (extra 1 untuk detect `has_next`)
  - Return: `(items, next_cursor, has_next)`
- Method `encode_cursor(value)` -> `str` (base64)
- Method `decode_cursor(cursor)` -> original value
- Support ascending dan descending order
- Works dengan SQLModel Select statement

**Cocok untuk**: feed, infinite scroll, real-time data yang sering insert

### 12b. OffsetPagination.py

- Class `offsetPagination`
- Method `paginate(query, page=1, per_page=20)`:
  - Apply `OFFSET` + `LIMIT`
  - Separate count query untuk total
  - Return: `(items, paginationMeta)`
- Method `calculate_offset(page, per_page)` -> `int`
- Max `per_page` configurable via config (prevent abuse)

**Config**:

| Config | Type | Default | Deskripsi |
|--------|------|---------|-----------|
| `pagination_default_limit` | `int` | `20` | Default items per page |
| `pagination_max_limit` | `int` | `100` | Max items per page (anti-abuse) |

**Cocok untuk**: admin panel, static data listing, search results

---

## Component #13: Auth Decorators

**Files**: 3 file dalam `components/decorators/`

**Responsibility**: Reusable auth validation decorators. Ga perlu nulis validasi header/cookie/token manual di setiap router.

### 13a. SessionDecorator.py

```python
def require_session(func):
    # extract session_id dari cookies
    # inject ke kwargs["session_id"]
    # raise unauthorized kalau ga ada
```

### 13b. AccessTokenDecorator.py

```python
def require_access_token(func):
    # extract Bearer token dari Authorization header
    # inject ke kwargs["access_token"]
    # raise unauthorized kalau ga ada atau format salah
```

### 13c. CookieDecorator.py

```python
def require_cookie(cookie_name: str):
    # parameterized decorator
    # extract cookie by name
    # inject ke kwargs[cookie_name]
    # raise unauthorized kalau ga ada
```

**Semua decorator**:
- Pakai `@wraps` dari `functools`
- Error handling via `exceptionFactory` dari components/exceptions
- Log blocked attempt via logger
- Inject extracted value ke kwargs, router function terima sebagai default parameter

**Pola di Router**:
```python
@router.get("/me")
@require_access_token
async def get_me(request: Request, access_token: str = "", ...):
    # access_token sudah di-inject, langsung pakai
    ...
```

---

## Component #14: Retry / Circuit Breaker

**File**: `components/database/RetryHandler.py`

**Responsibility**: Retry with exponential backoff untuk database/redis connections. Circuit breaker untuk prevent cascading failures.

**Key Design**:

### retryHandler

- Class `retryHandler`
- Constructor terima: `max_retries`, `base_delay`, `max_delay`, `backoff_factor`, logger
- Method `execute(async_fn, *args, **kwargs)`:
  - Coba jalankan `async_fn`
  - Kalau gagal, retry dengan exponential backoff: `delay = min(base_delay * (backoff_factor ** attempt), max_delay)`
  - Log setiap retry attempt: attempt number, delay, error detail
  - Setelah `max_retries` habis, raise last exception
- Method `execute_with_fallback(primary_fn, fallback_fn, *args, **kwargs)`:
  - Coba `primary_fn`, kalau gagal setelah semua retry, jalankan `fallback_fn`
  - Use case: Redis gagal -> fallback ke PG untuk rate limit data

### circuitBreaker

- Class `circuitBreaker`
- States: `CLOSED` (normal), `OPEN` (blocking), `HALF_OPEN` (testing)
- Constructor: `failure_threshold`, `recovery_timeout`, logger
- Logic:
  - CLOSED: forward request. Kalau gagal `failure_threshold` kali berturut-turut -> OPEN
  - OPEN: langsung reject tanpa coba. Setelah `recovery_timeout` detik -> HALF_OPEN
  - HALF_OPEN: coba 1 request. Kalau sukses -> CLOSED. Kalau gagal -> OPEN lagi
- Method `call(async_fn, *args, **kwargs)` -> wrap function dengan circuit breaker logic
- Log state transitions: `CLOSED -> OPEN`, `OPEN -> HALF_OPEN`, dll

**Config**:

| Config | Type | Default | Deskripsi |
|--------|------|---------|-----------|
| `retry_max_attempts` | `int` | `3` | Max retry |
| `retry_base_delay` | `float` | `1.0` | Initial delay (detik) |
| `retry_max_delay` | `float` | `30.0` | Max delay cap |
| `retry_backoff_factor` | `float` | `2.0` | Exponential multiplier |
| `circuit_failure_threshold` | `int` | `5` | Failures sebelum open |
| `circuit_recovery_timeout` | `int` | `60` | Detik sebelum half-open |

**Integration dengan PostgresEngine / RedisEngine**:
```python
# di postgresEngine.create_engine()
retry = retryHandler(config.retry_max_attempts, config.retry_base_delay, ...)
await retry.execute(self._do_create_engine)
```

---

## Component #15: Startup Readiness Gate

**File**: `components/health/ReadinessGate.py`

**Responsibility**: Block incoming traffic sampai semua critical dependencies ready. Beda dari health check yang cek ongoing — ini cek saat boot.

**Key Design**:
- Class `readinessGate`
- Constructor terima: list of `(name, check_fn)` tuples, logger
- Method `wait_until_ready(timeout=60, interval=2)`:
  - Loop jalankan semua `check_fn` setiap `interval` detik
  - Kalau semua return True -> ready, return
  - Kalau timeout tercapai -> raise `startupException` dengan detail mana yang gagal
  - Log progress: "Waiting for PostgreSQL... attempt 3/30"
- Method `register_check(name, check_fn)` — tambah check di runtime
- Method `is_ready()` -> `bool` — check sekali tanpa loop (untuk `/readyz` endpoint)

**Check Functions** (pre-built):
- `check_postgres(pg_engine)` -> `SELECT 1`
- `check_redis(redis_engine)` -> `PING`
- Custom: apapun async callable yang return `bool`

**Integration di lifespan**:
```python
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    await pg.create_engine()
    await redis.connect()

    gate = readinessGate([
        ("postgres", lambda: pg.health()),
        ("redis", lambda: redis.health()),
    ], logger=sys_log)
    await gate.wait_until_ready(timeout=config.startup_timeout)

    sys_log.startup("all dependencies ready")
    yield
    await pg.close()
    await redis.close()
```

**Kubernetes / Docker Integration**:
- Expose `GET /readyz` endpoint -> return 200 jika ready, 503 jika belum
- Beda dari `GET /health` (liveness) — readiness probe hanya True setelah gate passed
- Kubernetes pakai ini untuk `readinessProbe`, jadi pod ga terima traffic sebelum siap

**Config**:

| Config | Type | Default | Deskripsi |
|--------|------|---------|-----------|
| `startup_timeout` | `int` | `60` | Max detik tunggu semua dependency ready |
| `startup_check_interval` | `int` | `2` | Interval antar check (detik) |

---

## Component #16: Email Service

**Files**: `components/email/EmailService.py` + `components/email/EmailTemplateEngine.py` + `components/email/templates/*.mjml`

**Responsibility**: Async email sender via SMTP (Gmail) dengan MJML template rendering. Project tinggal call: template mana, data apa — selesai.

### Key Design

#### EmailTemplateEngine.py

- Class `emailTemplateEngine`
- Constructor terima: `templates_dir` (path ke folder `.mjml`)
- Method `render(template_name, **data)` -> `str` (HTML):
  - Load `.mjml` file dari `templates_dir`
  - Compile MJML ke HTML (pakai `mjml` Python package atau subprocess ke `mjml` CLI)
  - Inject variables ke HTML: replace `{{ variable_name }}` dengan actual value
  - Return rendered HTML string
- Method `list_templates()` -> `list[str]` — list semua available templates
- Template caching: compile MJML sekali, cache hasilnya. Kalau data beda cuma inject ulang variable-nya
- Variable injection pakai simple string replace atau `str.format_map` — ga perlu Jinja2 overhead

**Template Convention**:
- File naming: `PascalCase.mjml` (sesuai skill)
- Variables di template: `{{ user_name }}`, `{{ verification_code }}`, `{{ reset_link }}`
- Setiap template punya default subject line di comment baris pertama: `<!-- subject: Verify your email -->`

#### EmailService.py

- Class `emailService`
- Constructor terima: config, logger, template_engine
- Async karena SMTP send bisa blocking — pakai `aiosmtplib`
- Method `send(to, template_name, subject=None, **data)`:
  - Render template via `emailTemplateEngine.render(template_name, **data)`
  - Extract default subject dari template kalau `subject=None`
  - Send via SMTP (async)
  - Log result via `loggingSystem`
  - Return success/failure
- Method `send_raw(to, subject, html_body)`:
  - Kirim HTML tanpa template — untuk edge case
- Method `send_bulk(recipients: list[dict])`:
  - Batch send: `[{"to": "a@b.com", "template": "Welcome", "data": {...}}, ...]`
  - Sequential send (bukan parallel) untuk avoid Gmail rate limit
- Retry logic: kalau SMTP gagal, retry `email_retry_attempts` kali dengan backoff
- TIDAK raise exception kalau email gagal — log error, return False. Email failure ga boleh block auth flow

**Config**:

| Config | Type | Default | Deskripsi |
|--------|------|---------|-----------|
| `smtp_host` | `str` | `"smtp.gmail.com"` | SMTP server |
| `smtp_port` | `int` | `587` | SMTP port (TLS) |
| `smtp_user` | `str` | required | Gmail address |
| `smtp_password` | `str` | required | Gmail app password |
| `smtp_from_name` | `str` | `"No Reply"` | Sender display name |
| `smtp_from_email` | `str` | same as smtp_user | Sender email |
| `smtp_use_tls` | `bool` | `True` | Start TLS |
| `email_retry_attempts` | `int` | `3` | Retry kalau SMTP gagal |
| `email_templates_dir` | `str` | `"components/email/templates"` | Path ke MJML templates |

#### Template Files

**EmailVerification.mjml**:
```
<!-- subject: Verify your email address -->
```
- Variables: `{{ user_name }}`, `{{ verification_code }}`, `{{ expires_in }}`
- Content: greeting, 6-digit code, expiry notice

**PasswordReset.mjml**:
```
<!-- subject: Reset your password -->
```
- Variables: `{{ user_name }}`, `{{ reset_link }}`, `{{ expires_in }}`
- Content: greeting, reset button/link, expiry notice, "didn't request this?" notice

**Welcome.mjml**:
```
<!-- subject: Welcome to [app_name] -->
```
- Variables: `{{ user_name }}`, `{{ app_name }}`
- Content: welcome message, getting started tips

**Menambah template baru**: buat file `.mjml` baru di `templates/`, langsung bisa dipakai tanpa ubah kode. `emailTemplateEngine` auto-discover dari folder.

### Pola Penggunaan di Service

```python
# di AuthService atau VerificationService
await self._email.send(
    to=user.email,
    template_name="EmailVerification",
    user_name=user.name,
    verification_code=code,
    expires_in="1 hour",
)
```

Tinggal sebut template mana, data apa. Template engine handle compile + inject + render. Email service handle SMTP send.

### Pola Penggunaan dengan Background Task

```python
# di router — email dikirim di background, ga block response
bg.add_task(
    task_factory.execute,
    email_service.send,
    to=user.email,
    template_name="EmailVerification",
    user_name=user.name,
    verification_code=code,
    expires_in="1 hour",
)
```

**Dependency**: aiosmtplib, mjml (Python package atau CLI), config, logger

---

## Dependency Graph

```
components/config/          <-- standalone, pydantic-settings only
components/enums/           <-- standalone, pure Python enums
components/logger/          <-- depends on: config, enums (LogCategoryEnum)
components/uuid/            <-- standalone
components/exceptions/      <-- depends on: logger, enums (ErrorCodeEnum)
components/schemas/         <-- standalone (pydantic only)
components/database/        <-- depends on: config, logger, exceptions (RetryHandler included)
components/crypto/          <-- depends on: enums (CryptoAlgorithmEnum), config
components/http/            <-- depends on: config, logger, exceptions, uuid (correlation ID)
components/email/           <-- depends on: config, logger
components/pagination/      <-- depends on: config, schemas (pagination meta)
components/decorators/      <-- depends on: exceptions, logger
components/health/          <-- depends on: config, database, http, logger, enums (HealthStatusEnum)
components/middleware/       <-- depends on: config, logger, uuid, database (redis), exceptions
components/tasks/           <-- depends on: logger, database
```

**Build order** (dari yang paling independen):
1. config, enums, uuid, schemas (parallel, no internal deps)
2. logger (needs config, enums)
3. exceptions (needs logger, enums)
4. crypto (needs enums, config — Rust side terpisah)
5. database + RetryHandler (needs config, logger, exceptions)
6. http client, email service (needs config, logger)
7. pagination, decorators (needs config, schemas, exceptions)
8. health + ReadinessGate, middleware, tasks (needs database + logger + config + http + enums)

---

## Urutan Implementasi (Recommended)

| Phase | Component | Priority |
|-------|-----------|----------|
| 0 | Centralized Config (0) | CRITICAL — semua component baca config dari sini |
| 1 | Logger Factory (7) | CRITICAL — semua component depend on this |
| 2 | UUID Generator (8) | CRITICAL — middleware + semua ID generation |
| 3 | Exceptions (3) | CRITICAL — error handling foundation |
| 4 | Base Response Schema (11) | CRITICAL — standardisasi semua response format |
| 5 | PostgreSQL Engine (1) + Retry (14) | HIGH — core data layer + resilience |
| 6 | Redis Engine (2) + Retry (14) | HIGH — cache + rate limit + blacklist |
| 7 | HTTP Client Factory (10) | HIGH — inter-service + external API |
| 8 | Email Service (16) | HIGH — auth service butuh ini untuk verification + reset |
| 9 | Pagination Components (12) | HIGH — hampir semua endpoint butuh ini |
| 10 | Auth Decorators (13) | HIGH — semua protected endpoint butuh ini |
| 11 | Health Check (4) + Readiness Gate (15) | MEDIUM — operational readiness |
| 12 | Middleware (5) | MEDIUM — security + observability |
| 13 | Background Tasks (9) | MEDIUM — cleanup automation |
| 14 | Crypto Factory (6) | SEPARATE — Rust crate, build terpisah |

> Crypto Factory di-build sebagai project terpisah (Rust crate). Python wrapper-nya simple, yang berat di Rust side.

---

## Integration Point: main.py

Setelah semua components selesai, integration di `main.py` akan terlihat seperti:

```python
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
from fastapi import FastAPI

from src.domain.config.Settings import settings
from components.logger.LoggerFactory import loggerFactory
from components.logger.LoggingSystem import loggingSystem
from components.database.PostgresEngine import postgresEngine
from components.database.RedisEngine import redisEngine
from components.http.HttpClientFactory import httpClientFactory
from components.health.HealthCheck import healthCheck
from components.health.ReadinessGate import readinessGate
from components.middleware.MiddlewareRegistry import register_middlewares
from components.exceptions.ExceptionHandler import register_exception_handlers

# satu config object, semua components config included
config = settings()

logger = loggerFactory.create("main", level=config.log_level)
sys_log = loggingSystem(config.app_name)

pg = postgresEngine(config)
redis = redisEngine(config)
http = httpClientFactory(config, logger)
health = healthCheck(config, pg, redis, http)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    sys_log.startup("initializing engines")
    await pg.create_engine()
    await redis.connect()

    gate = readinessGate([
        ("postgres", pg.health),
        ("redis", redis.health),
    ], logger=sys_log)
    await gate.wait_until_ready(
        timeout=config.startup_timeout,
        interval=config.startup_check_interval,
    )
    sys_log.startup("all dependencies ready, accepting traffic")

    yield

    await http.close()
    await pg.close()
    await redis.close()
    sys_log.shutdown("engines disposed")


app = FastAPI(title=config.app_name, debug=config.debug, lifespan=lifespan)

register_exception_handlers(app)
register_middlewares(app, config)
app.include_router(health.router)
```

`config` = `settings()` yang inherit dari `componentSettings`. Satu object, semua config — database, redis, logger, health threshold, middleware, retry, pagination — langsung tersedia. Ga ada `dotenv.load()` manual.

---

## Crypto Rust: Build & Distribution Strategy

**Problem**: Sekarang kamu build per-project lewat venv, ribet dan rawan lupa saat deploy.

**Solution**: Build sekali, distribute sebagai wheel.

```
[Development Machine]
  |
  v
maturin build --release
  |
  v
dist/crypto_crate-0.1.0-cp314-cp314-manylinux_2_28_x86_64.whl
  |
  +---> Upload ke Private PyPI (recommended)
  |       poetry add crypto-crate --source private
  |
  +---> ATAU simpan di shared storage / git release
          poetry add https://github.com/.../releases/download/v0.1.0/crypto_crate-*.whl
```

**Di pyproject.toml project (Poetry)**:
```toml
[tool.poetry.dependencies]
crypto-crate = {url = "https://github.com/.../releases/download/v0.1.0/crypto_crate-0.1.0-cp314-cp314-manylinux_2_28_x86_64.whl"}
# ATAU kalau pakai private PyPI:
# crypto-crate = {version = "0.1.0", source = "private"}

# [tool.poetry.source]
# name = "private"
# url = "https://your-pypi.example.com/simple/"
# priority = "supplemental"
```

**CI/CD Build Matrix** (GitHub Actions):
- Build target: `manylinux_2_28_x86_64` (server), `macosx_11_0_arm64` (dev Mac)
- Python target: `cp314`
- Upload sebagai release artifact
- Bisa automate: push tag -> build wheel -> upload ke private PyPI

Dengan cara ini, deploy cukup `poetry install` — Rust binary sudah pre-compiled di dalam wheel, ga perlu Rust toolchain di production server.

---

## Poetry Setup (pyproject.toml)

Setiap project yang pakai components ini, `pyproject.toml`-nya:

```toml
[tool.poetry]
name = "auth-service"
version = "0.1.0"
description = ""
authors = [""]
packages = [{include = "src"}, {include = "components"}]

[tool.poetry.dependencies]
python = ">=3.14"
fastapi = ">=0.115.0"
uvicorn = {extras = ["standard"], version = ">=0.30.0"}
sqlmodel = ">=0.0.22"
sqlalchemy = {extras = ["asyncio"], version = ">=2.0.0"}
asyncpg = ">=0.30.0"
pydantic = ">=2.0.0"
pydantic-settings = ">=2.0.0"
redis = ">=5.0.0"
aiohttp = ">=3.9.0"
structlog = ">=24.0.0"
psutil = ">=6.0.0"
uuid-utils = ">=0.9.0"
aiosmtplib = ">=3.0.0"
mjml = ">=0.11.0"
alembic = ">=1.13.0"
psycopg = {extras = ["binary"], version = ">=3.1.0"}

[tool.poetry.group.dev.dependencies]
ruff = ">=0.6.0"
pytest = ">=8.0.0"
pytest-asyncio = ">=0.24.0"
httpx = ">=0.27.0"

[tool.ruff]
target-version = "py314"
line-length = 120

[tool.ruff.lint]
select = ["E", "W", "F", "I", "N", "UP", "B", "SIM", "TCH"]
ignore = ["N801"]

[tool.ruff.lint.isort]
known-first-party = ["src", "components"]
```

> **Note**: `packages` include both `src` dan `components` supaya import path works.
> `uuid-utils` dipilih karena Rust-backed (cepat) dan sudah support UUID7.
> `sqlmodel` menggantikan dataclass karena user prefer SQLModel.
> `httpx` di dev deps untuk testing HTTP endpoints.

---

## Notes

- Semua naming mengikuti skill: camelCase class, snake_case function, PascalCase file
- TIDAK ada `__init__.py` di folder manapun
- TIDAK ada docstring
- Semua config terpusat di `components/config/ComponentSettings.py` via pydantic-settings
- Project-level `Settings.py` cukup inherit `componentSettings` dan extend
- TIDAK pakai `python-dotenv` langsung — pydantic-settings handle `.env` loading
- Semua error WAJIB di-log (tidak ada silent error)
- Response field obfuscation diterapkan di exception response dan base response
- Import typing hanya untuk `Any`, sisanya pakai built-in (`list`, `dict`, `str | None`)
- Package manager: **Poetry** (bukan pip)
- `pyproject.toml` include `packages = [{include = "src"}, {include = "components"}]`
- `known-first-party` di ruff isort: `["src", "components"]`
- Total components: **17** (termasuk config #0 dan enums)
- Total files: **~40 Python files + MJML templates** di folder `components/`

## Component Summary

| # | Component | Files | Layer |
|---|-----------|-------|-------|
| 0 | Centralized Config | 2 | Foundation |
| - | Enums (shared) | 4 | Foundation |
| 1 | PostgreSQL Engine | 1 | Data |
| 2 | Redis Engine | 1 | Data |
| 3 | Exceptions | 4 | Foundation |
| 4 | Health Check + Readiness Gate | 2 | Ops |
| 5 | Middleware (6 types + registry) | 7 | Infra |
| 6 | Crypto Factory | 1 (+Rust crate) | Security |
| 7 | Logger Factory (3 categories) | 4 | Foundation |
| 8 | UUID Generator | 1 | Utility |
| 9 | Background Task Factory | 1 | Utility |
| 10 | HTTP Client Factory | 1 | Infra |
| 11 | Base Response Schema | 2 | Foundation |
| 12 | Pagination (cursor + offset) | 2 | Data |
| 13 | Auth Decorators | 3 | Security |
| 14 | Retry / Circuit Breaker | 1 | Resilience |
| 15 | Startup Readiness Gate | (included in #4) | Ops |
| 16 | Email Service | 2 + templates | Communication |