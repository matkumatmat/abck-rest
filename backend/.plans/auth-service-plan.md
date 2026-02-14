# Project Plan: Central Authentication Service

> Service: Authentication (port 8002)
> Stack: Python >= 3.14 | FastAPI | SQLModel | DDD
> Rule: PURE user, TIDAK ADA admin role
> Database: Shared dengan Admin+Payment (satu PostgreSQL)
> Components: Import dari `components/` (sudah direncanakan di plan sebelumnya)

---

## Overview

Authentication service yang menangani semua auth flow untuk user:
- Session-based authentication (cookie + Redis)
- JWT authentication (access + refresh token)
- API Key authentication (service-to-service)
- Email verification
- Password reset
- Multi-session management
- gRPC server untuk komunikasi dengan Admin+Payment service

---

## Folder Structure: `src/`

```
authentication/
├── components/                         # copy-paste dari components library
│   └── ...
├── src/
│   ├── main.py                         # FastAPI app, port 8002, lifespan
│   ├── Dependencies.py                 # DI provider (session, logger, services)
│   │
│   ├── domain/
│   │   ├── models/
│   │   │   ├── BaseModel.py            # shared fields: id, created_at, updated_at
│   │   │   ├── UserModel.py            # user entity
│   │   │   ├── SessionModel.py         # session per-device
│   │   │   ├── RefreshTokenModel.py    # JWT refresh tokens
│   │   │   ├── ApiKeyModel.py          # service-to-service keys
│   │   │   ├── VerificationModel.py    # email verification codes
│   │   │   └── PasswordResetModel.py   # password reset tokens
│   │   ├── enums/
│   │   │   ├── UserStatusEnum.py       # ACTIVE, INACTIVE, SUSPENDED, PENDING_VERIFICATION
│   │   │   ├── SessionStatusEnum.py    # ACTIVE, EXPIRED, REVOKED
│   │   │   ├── TokenTypeEnum.py        # ACCESS, REFRESH
│   │   │   ├── ApiKeyStatusEnum.py     # ACTIVE, REVOKED, EXPIRED
│   │   │   └── VerificationTypeEnum.py # EMAIL_VERIFY, PASSWORD_RESET
│   │   ├── config/
│   │   │   └── Settings.py             # extends componentSettings
│   │   └── types/
│   │       └── TokenPayload.py         # JWT payload dataclass
│   │
│   ├── application/
│   │   ├── services/
│   │   │   ├── AuthService.py          # register, login, logout orchestration
│   │   │   ├── SessionService.py       # session CRUD, multi-session, revoke
│   │   │   ├── TokenService.py         # JWT generate, refresh, decode, revoke
│   │   │   ├── VerificationService.py  # email verify, password reset flow
│   │   │   └── ApiKeyService.py        # API key create, validate, revoke
│   │   ├── interfaces/
│   │   │   ├── UserRepositoryInterface.py
│   │   │   ├── SessionRepositoryInterface.py
│   │   │   ├── RefreshTokenRepositoryInterface.py
│   │   │   ├── ApiKeyRepositoryInterface.py
│   │   │   ├── VerificationRepositoryInterface.py
│   │   │   ├── PasswordResetRepositoryInterface.py
│   │   │   └── UnitOfWorkInterface.py  # atomic: register, login
│   │   └── schemas/
│   │       ├── AuthSchema.py           # register, login request/response
│   │       ├── SessionSchema.py        # session list, revoke request/response
│   │       ├── TokenSchema.py          # token refresh request/response
│   │       ├── VerificationSchema.py   # verify email, reset password request/response
│   │       └── ApiKeySchema.py         # API key request/response
│   │
│   └── infrastructure/
│       ├── repositories/
│       │   ├── UserRepository.py
│       │   ├── SessionRepository.py
│       │   ├── RefreshTokenRepository.py
│       │   ├── ApiKeyRepository.py
│       │   ├── VerificationRepository.py
│       │   └── PasswordResetRepository.py
│       ├── postgres/
│       │   └── PostgresUnitOfWork.py   # UoW implementation
│       ├── grpc/
│       │   ├── AuthGrpcServer.py       # gRPC server (validate session/token, get user)
│       │   └── AuthGrpcServicer.py     # gRPC method implementations
│       └── routers/
│           └── v1/
│               ├── AuthRouter.py       # POST /register, /login, /logout
│               ├── SessionRouter.py    # GET /sessions, DELETE /sessions/{id}
│               ├── TokenRouter.py      # POST /token/refresh
│               └── VerificationRouter.py # POST /verify-email, /forgot-password, /reset-password
│
├── proto/
│   └── auth.proto                      # shared gRPC proto (juga dipakai Admin+Payment)
├── alembic/
│   ├── env.py                          # Alembic config, import semua models
│   ├── script.py.mako                  # template migration file
│   └── versions/                       # auto-generated migration files
├── alembic.ini                         # Alembic config (DB URL dari ENV)
├── md/
│   └── ...
├── pyproject.toml
├── Dockerfile
├── docker-compose.yml                  # dev only (PG + Redis + service)
└── .env.example
```

TIDAK ada `__init__.py`. TIDAK ada docstring. TIDAK ada README.md di root.

---

## Domain Layer

### BaseModel.py — Shared Fields

Semua model inherit dari sini. Ga perlu tulis `id`, `created_at`, `updated_at` berulang-ulang.

```python
from datetime import datetime
from sqlmodel import SQLModel, Field
from components.uuid.UuidGenerator import uuidGenerator


class baseModel(SQLModel):
    id: str = Field(default_factory=uuidGenerator.create, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    def touch(self) -> None:
        self.updated_at = datetime.utcnow()

    def apply_update(self, data: dict) -> None:
        for key, value in data.items():
            if value is not None and hasattr(self, key):
                setattr(self, key, value)
        self.touch()
```

Semua domain model inherit `baseModel` dan punya `id` (UUID7), `created_at`, `updated_at` otomatis.

---

### UserModel.py

```python
class userModel(baseModel, table=True):
    __tablename__ = "users"

    email: str = Field(unique=True, index=True)
    password_hash: str
    name: str
    status: userStatusEnum = Field(default=userStatusEnum.PENDING_VERIFICATION)

    # --- domain logic ---
    def is_active(self) -> bool
    def is_verified(self) -> bool
    def __bool__(self) -> bool          # True jika ACTIVE
    def activate(self) -> None          # PENDING -> ACTIVE
    def suspend(self) -> None           # -> SUSPENDED
    def deactivate(self) -> None        # -> INACTIVE
    def update_password(self, new_hash: str) -> None
    def validate_email(self) -> None    # format check via model_validator
```

**Domain logic di model, bukan di service**:
- Status transition (`activate`, `suspend`, `deactivate`) di model
- Password update di model (termasuk touch `updated_at`)
- Email validation via Pydantic `model_validator`

---

### SessionModel.py

```python
class sessionModel(baseModel, table=True):
    __tablename__ = "sessions"

    user_id: str = Field(foreign_key="users.id", index=True)
    ip_address: str
    user_agent: str
    status: sessionStatusEnum = Field(default=sessionStatusEnum.ACTIVE)
    expires_at: datetime
    last_activity: datetime = Field(default_factory=datetime.utcnow)

    # --- domain logic ---
    def is_expired(self) -> bool        # expires_at < now
    def is_active(self) -> bool         # status ACTIVE dan belum expired
    def __bool__(self) -> bool          # True jika active + not expired
    def revoke(self) -> None            # -> REVOKED
    def refresh_activity(self) -> None  # update last_activity
    def extend(self, duration_seconds: int) -> None  # perpanjang expires_at
```

Session juga disimpan di **Redis** (untuk fast lookup) + **PostgreSQL** (untuk persistence dan multi-session listing). Redis sebagai primary read, PG sebagai source of truth.

---

### RefreshTokenModel.py

```python
class refreshTokenModel(baseModel, table=True):
    __tablename__ = "refresh_tokens"

    user_id: str = Field(foreign_key="users.id", index=True)
    token_hash: str = Field(unique=True)
    session_id: str = Field(foreign_key="sessions.id")
    expires_at: datetime
    revoked: bool = Field(default=False)

    # --- domain logic ---
    def is_valid(self) -> bool          # not revoked dan not expired
    def __bool__(self) -> bool          # same as is_valid
    def revoke(self) -> None            # set revoked = True
```

Refresh token di-hash di DB (bukan plaintext). Tied ke session — kalau session revoked, refresh token juga revoked.

---

### ApiKeyModel.py

```python
class apiKeyModel(baseModel, table=True):
    __tablename__ = "api_keys"

    name: str                            # human-readable label
    key_hash: str = Field(unique=True)   # hashed API key
    key_prefix: str                      # first 8 chars for identification
    service_name: str                    # which service owns this key
    status: apiKeyStatusEnum = Field(default=apiKeyStatusEnum.ACTIVE)
    expires_at: datetime | None = None   # None = never expires
    last_used_at: datetime | None = None

    # --- domain logic ---
    def is_valid(self) -> bool           # ACTIVE + not expired
    def __bool__(self) -> bool
    def revoke(self) -> None
    def record_usage(self) -> None       # update last_used_at
```

API key: generate -> hash -> simpan hash di DB. Return plaintext key SEKALI saat create. Prefix untuk identifikasi tanpa expose full key.

---

### VerificationModel.py

```python
class verificationModel(baseModel, table=True):
    __tablename__ = "verifications"

    user_id: str = Field(foreign_key="users.id", index=True)
    code_hash: str                       # hashed verification code
    verification_type: verificationTypeEnum
    expires_at: datetime
    used: bool = Field(default=False)

    # --- domain logic ---
    def is_valid(self) -> bool           # not used dan not expired
    def __bool__(self) -> bool
    def mark_used(self) -> None
```

---

### PasswordResetModel.py

```python
class passwordResetModel(baseModel, table=True):
    __tablename__ = "password_resets"

    user_id: str = Field(foreign_key="users.id", index=True)
    token_hash: str = Field(unique=True)
    expires_at: datetime
    used: bool = Field(default=False)

    # --- domain logic ---
    def is_valid(self) -> bool
    def __bool__(self) -> bool
    def mark_used(self) -> None
```

---

### Enums

| Enum | Values |
|------|--------|
| `userStatusEnum` | `ACTIVE`, `INACTIVE`, `SUSPENDED`, `PENDING_VERIFICATION` |
| `sessionStatusEnum` | `ACTIVE`, `EXPIRED`, `REVOKED` |
| `tokenTypeEnum` | `ACCESS`, `REFRESH` |
| `apiKeyStatusEnum` | `ACTIVE`, `REVOKED`, `EXPIRED` |
| `verificationTypeEnum` | `EMAIL_VERIFY`, `PASSWORD_RESET` |

---

### Settings.py — Auth-Specific Config

```python
from components.config.ComponentSettings import componentSettings

class settings(componentSettings):
    # -- App --
    app_name: str = "auth-service"
    app_port: int = 8002
    debug: bool = False

    # -- JWT --
    jwt_secret: str
    jwt_access_expires: int = 900          # 15 menit (detik)
    jwt_refresh_expires: int = 604800      # 7 hari (detik)
    jwt_algorithm: str = "HS256"

    # -- Session --
    session_expires: int = 86400           # 24 jam (detik)
    session_cookie_name: str = "sid"
    session_cookie_secure: bool = True
    session_cookie_httponly: bool = True
    session_cookie_samesite: str = "lax"
    session_max_per_user: int = 5          # max concurrent sessions

    # -- Verification --
    verification_code_length: int = 6
    verification_expires: int = 3600       # 1 jam
    password_reset_expires: int = 1800     # 30 menit

    # -- API Key --
    api_key_prefix_length: int = 8
    api_key_length: int = 48

    # -- Rate Limit (login specific) --
    login_rate_limit_window: int = 300     # 5 menit
    login_rate_limit_max: int = 5          # max 5 attempts per window

    # -- gRPC --
    grpc_port: int = 50051
```

Semua config dari ENV. `componentSettings` sudah handle database, redis, logger, retry, dll. Auth service cuma extend yang spesifik.

---

## Application Layer

### Services — Thin Orchestration

Semua service mengikuti prinsip **thin service**: hanya orchestrate, logic validasi/transform di domain model.

#### AuthService.py

| Method | Flow |
|--------|------|
| `register(data)` | validate email uniqueness -> hash password (crypto) -> create user (PENDING) -> create verification code -> (bg task: `emailService.send("EmailVerification", ...)`) -> return user |
| `login(data)` | find user by email -> verify password (crypto) -> check rate limit -> check status ACTIVE -> create session (DB + Redis) -> generate JWT pair -> **set CSRF cookie** -> return tokens + session |
| `logout(session_id, access_token)` | find session -> revoke session (DB + Redis) -> revoke associated refresh tokens -> **blacklist current access token (Redis)** -> return |

**Register dan Login pakai UoW** karena multiple repo operations harus atomic:
- Register: save user + save verification = atomic
- Login: save session + save refresh token = atomic

#### SessionService.py

| Method | Flow |
|--------|------|
| `list_sessions(user_id)` | fetch all active sessions for user -> return list |
| `revoke_session(user_id, session_id)` | find session -> verify ownership -> revoke (DB + Redis) -> revoke associated refresh tokens |
| `revoke_all_sessions(user_id)` | fetch all active sessions -> revoke all (DB + Redis) -> revoke all refresh tokens |
| `validate_session(session_id)` | check Redis first -> fallback PG -> check expired -> refresh activity -> return user_id |

#### TokenService.py

| Method | Flow |
|--------|------|
| `generate_pair(user_id, session_id)` | create access token (stateless JWT) + create refresh token (hashed, saved DB) -> return pair |
| `refresh(refresh_token)` | find by hash -> check valid -> check session still active -> revoke old -> generate new pair (token rotation) |
| `decode_access(token)` | decode JWT -> validate expiry -> **check blacklist (Redis)** -> return payload |
| `revoke_by_session(session_id)` | revoke all refresh tokens tied to session + **blacklist active access token** |
| `blacklist_access(token, expires_at)` | add JWT `jti` ke Redis blacklist dengan TTL = remaining lifetime |
| `is_blacklisted(jti)` | check Redis apakah `jti` ada di blacklist |

**Token rotation**: setiap kali refresh, old refresh token di-revoke dan bikin baru. Prevent replay attack.

**JWT Blacklist** (Redis): Access token itu stateless — sekali issued, valid sampai expired. Masalahnya: kalau user logout, ganti password, atau di-suspend, access token masih bisa dipakai. Solusi: blacklist di Redis.

```
Blacklist key: jwt_blacklist:{jti}
Value: "1"
TTL: sisa lifetime access token (jwt_access_expires - elapsed)
```

**Kapan access token di-blacklist**:
- User logout -> blacklist current access token
- User ganti password -> blacklist semua access token user (via session revoke)
- User di-suspend -> blacklist semua access token user
- Token refresh -> blacklist old access token

**Kenapa Redis bukan PG**: lookup harus cepat — setiap request yang pakai JWT harus check blacklist. Redis O(1) lookup, TTL auto-cleanup (ga perlu background task).

**`decode_access` flow lengkap**:
1. Decode JWT, check signature + expiry
2. Extract `jti` dari payload
3. Check `is_blacklisted(jti)` di Redis
4. Kalau blacklisted -> raise `UNAUTHORIZED`
5. Kalau valid -> return payload

**JWT Payload** (`domain/types/TokenPayload.py`):
```python
@dataclass
class tokenPayload:
    sub: str          # user_id
    sid: str          # session_id
    jti: str          # unique token ID (UUID7) — untuk blacklist
    exp: int          # expiry timestamp
    iat: int          # issued at
    typ: str          # "access" atau "refresh"
```

`jti` (JWT ID) wajib ada di setiap access token supaya bisa di-blacklist secara individual.

#### VerificationService.py

| Method | Flow |
|--------|------|
| `create_email_verification(user_id)` | generate code -> hash -> save DB -> (bg task: `emailService.send("EmailVerification", ...)`) |
| `verify_email(user_id, code)` | find verification -> verify hash -> mark used -> activate user -> (bg task: `emailService.send("Welcome", ...)`) |
| `create_password_reset(email)` | find user -> generate token -> hash -> save DB -> (bg task: `emailService.send("PasswordReset", ...)`) |
| `reset_password(token, new_password)` | find reset by hash -> check valid -> hash new password -> update user -> mark used -> revoke all sessions + **blacklist all access tokens** |

**VerificationService inject `emailService`** via constructor. Email dikirim di background task supaya ga block response.

```python
class verificationService:
    def __init__(
        self,
        uow: unitOfWorkInterface,
        email: emailService,
        crypto: cryptoFactory,
        logger: loggerPort,
    ) -> None:
        self._uow = uow
        self._email = email
        self._crypto = crypto
        self._logger = logger

    async def create_email_verification(self, user_id: str, bg: BackgroundTasks) -> None:
        code = generate_random_code(self._config.verification_code_length)
        code_hash = self._crypto.hash_data(code)
        async with self._uow as uow:
            user = await uow.users.find_by_id(user_id)
            verification = verificationModel(
                user_id=user_id,
                code_hash=code_hash,
                verification_type=verificationTypeEnum.EMAIL_VERIFY,
                expires_at=...,
            )
            await uow.verifications.save(verification)
            await uow.commit()

        bg.add_task(
            self._email.send,
            to=user.email,
            template_name="EmailVerification",
            user_name=user.name,
            verification_code=code,
            expires_in="1 hour",
        )
```

**Reset password juga revoke semua session** — security measure.

#### ApiKeyService.py

| Method | Flow |
|--------|------|
| `create(name, service_name, expires_at)` | generate key -> hash -> save DB with prefix -> return plaintext key (SEKALI) |
| `validate(api_key)` | extract prefix -> find by prefix -> verify hash -> check valid -> record usage -> return service info |
| `revoke(key_id)` | find -> revoke |
| `list(service_name)` | fetch all keys for service (tanpa expose hash) |

---

### Interfaces (Repository Contracts)

| Interface | Key Methods |
|-----------|-------------|
| `userRepositoryInterface` | `find_by_id`, `find_by_email`, `save`, `update` |
| `sessionRepositoryInterface` | `find_by_id`, `find_by_user_id`, `find_active_by_user_id`, `save`, `update`, `delete_expired` |
| `refreshTokenRepositoryInterface` | `find_by_hash`, `find_by_session_id`, `save`, `revoke_by_session`, `delete_expired` |
| `apiKeyRepositoryInterface` | `find_by_prefix`, `find_by_id`, `find_by_service`, `save`, `update` |
| `verificationRepositoryInterface` | `find_by_user_and_type`, `save`, `update`, `delete_expired` |
| `passwordResetRepositoryInterface` | `find_by_hash`, `save`, `update`, `delete_expired` |

Semua interface punya `delete_expired` untuk background task cleanup.

---

### UnitOfWork

| Operation | Repositories Involved |
|-----------|----------------------|
| Register | `users` + `verifications` |
| Login | `sessions` + `refresh_tokens` |
| Reset Password | `password_resets` + `users` + `sessions` + `refresh_tokens` |
| Revoke All Sessions | `sessions` + `refresh_tokens` |

```python
class unitOfWorkInterface(ABC):
    users: userRepositoryInterface
    sessions: sessionRepositoryInterface
    refresh_tokens: refreshTokenRepositoryInterface
    verifications: verificationRepositoryInterface
    password_resets: passwordResetRepositoryInterface

    async def __aenter__(self) -> Self
    async def __aexit__(self, ...) -> None
    async def commit(self) -> None
    async def rollback(self) -> None
```

---

### Schemas — Request/Response

Semua request inherit `baseRequest` (strict mode). Semua response inherit `baseResponse` (camelCase alias + from_attributes). Obfuscation diterapkan pada field sensitif.

#### AuthSchema.py

**Request**:
- `registerRequest`: `email`, `password`, `name`
- `loginRequest`: `email`, `password`, `user_agent` (auto dari header), `ip_address` (auto dari request)

**Response**:
- `authResponse`: `_at` (access_token), `_rt` (refresh_token), `_exp` (expires_in)
- `registerResponse`: `_uid` (user_id), `_em` (email), `_st` (status)

#### SessionSchema.py

**Request**:
- `revokeSessionRequest`: `session_id`

**Response**:
- `sessionItemResponse`: `_sid` (session_id), `_ip` (ip_address), `_ua` (user_agent), `_la` (last_activity), `_ca` (created_at)
- `sessionListResponse`: `sessions: list[sessionItemResponse]`, `total: int`

#### TokenSchema.py

**Request**:
- `refreshTokenRequest`: `refresh_token`

**Response**:
- `tokenResponse`: `_at` (access_token), `_rt` (new refresh_token), `_exp` (expires_in)

#### VerificationSchema.py

**Request**:
- `verifyEmailRequest`: `code`
- `forgotPasswordRequest`: `email`
- `resetPasswordRequest`: `token`, `new_password`

**Response**:
- `verificationResponse`: `success: bool`, `_m` (message)

#### ApiKeySchema.py

**Request**:
- `createApiKeyRequest`: `name`, `service_name`, `expires_at` (optional)

**Response**:
- `apiKeyCreatedResponse`: `_k` (plaintext key — hanya ditampilkan SEKALI), `_pfx` (prefix), `name`
- `apiKeyItemResponse`: `_kid` (key_id), `_pfx` (prefix), `name`, `service_name`, `_lu` (last_used_at), `_st` (status)

---

## Infrastructure Layer

### Repositories

Semua repository inject `AsyncSession` via constructor. Implementasi SQLModel queries.

Pattern per repository:
```python
class userRepository(userRepositoryInterface):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
    # ... implement all interface methods
```

### PostgresUnitOfWork

```python
class postgresUnitOfWork(unitOfWorkInterface):
    def __init__(self, session_factory) -> None:
        self._session_factory = session_factory

    async def __aenter__(self):
        self._session = self._session_factory()
        self.users = userRepository(self._session)
        self.sessions = sessionRepository(self._session)
        self.refresh_tokens = refreshTokenRepository(self._session)
        self.verifications = verificationRepository(self._session)
        self.password_resets = passwordResetRepository(self._session)
        return self
```

### Routers (v1)

| Router | Endpoints | Auth Required |
|--------|-----------|---------------|
| **AuthRouter** | `POST /v1/auth/register` | No |
| | `POST /v1/auth/login` | No (rate limited) |
| | `POST /v1/auth/logout` | Yes (session decorator) |
| **SessionRouter** | `GET /v1/sessions` | Yes (access token decorator) |
| | `DELETE /v1/sessions/{id}` | Yes (access token decorator) |
| | `DELETE /v1/sessions` | Yes — revoke all |
| **TokenRouter** | `POST /v1/token/refresh` | No (refresh token in body) |
| **VerificationRouter** | `POST /v1/verify-email` | Yes (access token) |
| | `POST /v1/forgot-password` | No |
| | `POST /v1/reset-password` | No (token in body) |

Auth decorators dari `components/decorators/` — ga nulis validasi manual di router.

### gRPC Server

**Proto** (`proto/auth.proto`):

```protobuf
syntax = "proto3";
package auth;

service AuthService {
    rpc ValidateSession (ValidateSessionRequest) returns (ValidateSessionResponse);
    rpc ValidateToken (ValidateTokenRequest) returns (ValidateTokenResponse);
    rpc ValidateApiKey (ValidateApiKeyRequest) returns (ValidateApiKeyResponse);
    rpc GetUser (GetUserRequest) returns (GetUserResponse);
}

message ValidateSessionRequest { string session_id = 1; }
message ValidateSessionResponse { bool valid = 1; string user_id = 2; }

message ValidateTokenRequest { string access_token = 1; }
message ValidateTokenResponse { bool valid = 1; string user_id = 2; }

message ValidateApiKeyRequest { string api_key = 1; }
message ValidateApiKeyResponse { bool valid = 1; string service_name = 2; }

message GetUserRequest { string user_id = 1; }
message GetUserResponse { string user_id = 1; string email = 2; string name = 3; string status = 4; }
```

**AuthGrpcServer.py**: Start gRPC server di port `grpc_port` (50051) — dijalankan bersamaan dengan FastAPI di lifespan.

**AuthGrpcServicer.py**: Implement methods, pakai service layer yang sama (SessionService, TokenService, dll).

---

## Background Tasks (via components)

| Task | Trigger | Logic |
|------|---------|-------|
| Session cleanup | `POST /auth/login` (per X logins) atau scheduled | `backgroundTaskFactory.cleanup(sessionModel, "expires_at", now)` |
| Refresh token cleanup | same trigger | `backgroundTaskFactory.cleanup(refreshTokenModel, "expires_at", now)` |
| Verification cleanup | `POST /verify-email` | `backgroundTaskFactory.cleanup(verificationModel, "expires_at", now)` |
| Password reset cleanup | `POST /reset-password` | `backgroundTaskFactory.cleanup(passwordResetModel, "expires_at", now)` |
| Redis session sync | Periodic | Sync expired sessions dari Redis ke PG status |
| Send verification email | `POST /register` | `emailService.send(to, "EmailVerification", user_name=..., verification_code=..., expires_in=...)` |
| Send reset email | `POST /forgot-password` | `emailService.send(to, "PasswordReset", user_name=..., reset_link=..., expires_in=...)` |
| Send welcome email | After verify email success | `emailService.send(to, "Welcome", user_name=..., app_name=...)` |

Semua email sending dijalankan via `BackgroundTasks.add_task()` — ga block response. Cleanup pakai `components/tasks/BackgroundTaskFactory.py`.

---

## Rate Limiting (Login)

Login rate limit pakai `components/middleware/RateLimitWriter.py` + custom logic:

- Key: `login:{email}:{window}`
- Window: `login_rate_limit_window` (default 5 menit)
- Max: `login_rate_limit_max` (default 5 attempts)
- Di Redis: increment counter per login attempt
- Di AuthService: check counter sebelum verify password
- Kalau exceeded: raise `exceptionFactory` dengan code `RATE_LIMITED`
- Counter reset setelah successful login

---

## Session Strategy: Redis + PostgreSQL

```
Login
  |
  ├──> PostgreSQL: INSERT session row (source of truth, multi-session listing)
  └──> Redis: SET session:{id} = {user_id, ip, ua, expires} TTL=session_expires
         (fast validation, primary read)

Validate Session (hot path)
  |
  ├──> Redis GET session:{id}     <-- cepat, O(1)
  │      found? -> return user_id
  │      not found? ──┐
  │                    v
  └──> PostgreSQL SELECT         <-- fallback, check if still valid
         found + active? -> re-cache ke Redis -> return user_id
         not found / expired? -> return invalid

Revoke Session
  |
  ├──> PostgreSQL: UPDATE status = REVOKED
  └──> Redis: DELETE session:{id}

Session Cleanup (background)
  |
  ├──> PostgreSQL: DELETE WHERE expires_at < now AND status != ACTIVE
  └──> Redis: keys expired otomatis via TTL
```

---

## JWT Blacklist Strategy: Redis

```
Blacklist Access Token (logout, password change, suspend)
  |
  └──> Redis: SET jwt_blacklist:{jti} = "1" EX={remaining_lifetime}
         (auto-expire via TTL, ga perlu cleanup)

Validate Access Token (setiap request)
  |
  ├──> 1. Decode JWT (signature + expiry check)
  ├──> 2. Extract jti dari payload
  ├──> 3. Redis EXISTS jwt_blacklist:{jti}
  │         exists? -> REJECT 401
  │         not exists? -> VALID, continue
  └──> 4. Return payload
```

**Key format**: `jwt_blacklist:{jti}` — `jti` adalah UUID7 unik per access token.

**TTL**: Sisa lifetime token. Misal access token expires 15 menit, sudah jalan 5 menit, maka TTL blacklist = 10 menit. Setelah token expired, entry Redis otomatis hilang — ga membengkak.

**Worst case size**: max concurrent users x max sessions per user x 1 key. Misal 10.000 users x 5 sessions = 50.000 keys. Tiap key ~50 bytes. Total ~2.5MB di Redis. Negligible.

---

## CSRF Protection Strategy

CSRF attack hanya relevan untuk **session-based auth** (cookie auto-attached oleh browser). JWT via `Authorization` header aman karena browser ga auto-attach custom headers.

**Flow**:
```
Login Success
  |
  └──> Set 2 cookies:
       1. sid (session ID) - HttpOnly=True, Secure, SameSite=Lax
       2. _csrf (CSRF token) - HttpOnly=False, Secure, SameSite=Lax
          (HttpOnly=False supaya frontend JS bisa baca dan attach ke header)

State-changing Request (POST/PUT/DELETE) dengan Session Cookie
  |
  ├──> Browser auto-kirim cookie: sid + _csrf
  ├──> Frontend manually attach header: X-CSRF-Token = value dari _csrf cookie
  ├──> CsrfMiddleware compare: header X-CSRF-Token == cookie _csrf
  │      match? -> continue
  │      mismatch? -> REJECT 403 CSRF_INVALID
  └──> SessionDecorator validate session as usual
```

**CSRF token generation**: `cryptoFactory.hash_data(session_id + csrf_secret)` — deterministic per session, ga perlu simpan terpisah.

**Exempt paths** (ga perlu CSRF):
- `POST /v1/auth/login` — belum ada session
- `POST /v1/auth/register` — belum ada session
- `POST /v1/token/refresh` — pakai refresh token di body, bukan session cookie
- `POST /v1/forgot-password` — public endpoint
- Safe methods (GET, HEAD, OPTIONS) — di-skip otomatis

Middleware ini dari `components/middleware/CsrfMiddleware.py` — tinggal enable di config.

---

## Database Migration: Alembic

### Setup

```
authentication/
├── alembic/
│   ├── env.py              # Alembic env, import semua SQLModel models
│   ├── script.py.mako      # migration file template
│   └── versions/            # auto-generated migration files
│       ├── 001_initial_users.py
│       ├── 002_sessions_and_tokens.py
│       └── ...
└── alembic.ini              # config, DB URL dari ENV
```

### alembic.ini

```ini
[alembic]
script_location = alembic
# sqlalchemy.url di-override di env.py dari ENV
```

### env.py — Key Points

```python
from src.domain.config.Settings import settings
from src.domain.models.UserModel import userModel
from src.domain.models.SessionModel import sessionModel
from src.domain.models.RefreshTokenModel import refreshTokenModel
from src.domain.models.ApiKeyModel import apiKeyModel
from src.domain.models.VerificationModel import verificationModel
from src.domain.models.PasswordResetModel import passwordResetModel
from sqlmodel import SQLModel

config = settings()
target_metadata = SQLModel.metadata
# set sqlalchemy.url from config.database_url (replace +asyncpg with +psycopg for sync alembic)
```

**PENTING**: Alembic jalannya **synchronous**. Database URL harus pakai driver sync (`postgresql+psycopg` atau `postgresql://`), bukan `postgresql+asyncpg`. Di `env.py`, replace driver string otomatis:

```python
sync_url = config.database_url.replace("+asyncpg", "+psycopg")
```

### Migration Strategy

| Kapan | Command | Deskripsi |
|-------|---------|-----------|
| Bikin migration baru | `alembic revision --autogenerate -m "add_xyz"` | Auto-detect perubahan model |
| Apply migration (dev) | `alembic upgrade head` | Apply semua pending migrations |
| Apply migration (prod) | `alembic upgrade head` di CI/CD pipeline | Sebelum deploy new version |
| Rollback 1 step | `alembic downgrade -1` | Emergency rollback |
| Check current state | `alembic current` | Lihat revision sekarang |
| Check pending | `alembic history` | Lihat semua revisions |

### Rules

- Migration file JANGAN diedit setelah di-push ke git (kecuali belum di-apply di prod)
- Setiap migration punya `upgrade()` dan `downgrade()` — harus reversible
- Nama migration deskriptif: `add_api_keys_table`, `add_index_sessions_user_id`
- Migration dijalankan di CI/CD **sebelum** deploy app baru
- JANGAN pakai `alembic upgrade head` di app startup (race condition kalau multiple instances)
- Shared database (auth + admin+payment): koordinasi migration — masing-masing service punya alembic sendiri tapi JANGAN conflict table names
- Test migration: `upgrade head` lalu `downgrade base` lalu `upgrade head` lagi — harus clean

### Docker Integration

Di `docker-compose.yml` (dev), migration dijalankan sebagai separate step:

```yaml
services:
  migrate:
    build: .
    command: alembic upgrade head
    env_file: .env
    depends_on:
      postgres:
        condition: service_healthy

  authentication:
    build: .
    command: uvicorn src.main:app --host 0.0.0.0 --port 8002
    depends_on:
      migrate:
        condition: service_completed_successfully
```

Service `authentication` baru start setelah `migrate` selesai.

### pyproject.toml Dependency

```toml
alembic = ">=1.13.0"
psycopg = {extras = ["binary"], version = ">=3.1.0"}  # sync driver untuk alembic
```

---

## Components Usage Map

| Component | Dipakai di |
|-----------|-----------|
| `ComponentSettings` | `Settings.py` (inherit) |
| `postgresEngine` | `main.py` (lifespan), `Dependencies.py` |
| `redisEngine` | `main.py` (lifespan), `SessionService`, `TokenService` (JWT blacklist), `RateLimitWriter` |
| `loggerFactory` | Semua service, semua repository, grpc |
| `loggingSystem` | `main.py` startup/shutdown |
| `loggingDatabase` | Repository layer |
| `loggingUserBehaviour` | `AuthService` (login, register, logout events) |
| `uuidGenerator` | `BaseModel.py` (id generation) |
| `cryptoFactory` | `AuthService` (password: Python argon2-cffi), `TokenService` (hash: Rust BLAKE3), `ApiKeyService` (hash: Rust BLAKE3), encryption (Rust AES-256-GCM) |
| `exceptionFactory` via handlers | `ExceptionHandler` registered di `main.py` |
| `healthCheck` + `readinessGate` | `main.py`, `/health` endpoint |
| `register_middlewares` | `main.py` (CORS, correlation ID, request log, trusted host, blacklist, **CSRF**) |
| `backgroundTaskFactory` | `AuthRouter`, `VerificationRouter` (cleanup + email sending) |
| `httpClientFactory` | `HealthCheck` (external API ping), inter-service calls |
| `emailService` | `VerificationService` (send verification, reset, welcome emails via SMTP) |
| `emailTemplateEngine` | `emailService` internal (MJML compile + variable injection) |
| `retryHandler` | `postgresEngine`, `redisEngine` internal |
| `cursorPagination` | `SessionRouter` (list sessions kalau banyak) |
| `require_session` decorator | `AuthRouter` logout |
| `require_access_token` decorator | `SessionRouter`, `VerificationRouter` |
| `successResponse` | Semua router response wrapper |
| `paginationMeta` | Session listing |

**Semua component terpakai.** Ga ada yang mubazir.

---

## Database Schema Overview

```
┌─────────────────┐
│     users        │
├─────────────────┤
│ id (PK, UUID7)  │
│ email (UNIQUE)  │
│ password_hash   │
│ name            │
│ status (ENUM)   │
│ created_at      │
│ updated_at      │
└────────┬────────┘
         │ 1:N
    ┌────┴──────────────────────────┐
    │              │                │
┌───▼────┐  ┌─────▼──────┐  ┌─────▼──────────┐
│sessions │  │verifications│  │password_resets  │
├─────────┤  ├────────────┤  ├────────────────┤
│ id (PK) │  │ id (PK)    │  │ id (PK)        │
│ user_id │  │ user_id    │  │ user_id        │
│ ip_addr │  │ code_hash  │  │ token_hash     │
│ user_ag │  │ type (ENUM)│  │ expires_at     │
│ status  │  │ expires_at │  │ used           │
│ expires │  │ used       │  │ created_at     │
│ last_act│  │ created_at │  │ updated_at     │
│ created │  └────────────┘  └────────────────┘
│ updated │
└────┬────┘
     │ 1:N
┌────▼──────────┐
│refresh_tokens  │
├───────────────┤
│ id (PK)       │
│ user_id       │
│ session_id    │
│ token_hash    │
│ expires_at    │
│ revoked       │
│ created_at    │
│ updated_at    │
└───────────────┘

┌──────────────┐
│  api_keys     │  (no FK to users — ini service-level, bukan user-level)
├──────────────┤
│ id (PK)      │
│ name         │
│ key_hash     │
│ key_prefix   │
│ service_name │
│ status (ENUM)│
│ expires_at   │
│ last_used_at │
│ created_at   │
│ updated_at   │
└──────────────┘
```

**Indexes** (selain PK):
- `users.email` — UNIQUE + INDEX
- `sessions.user_id` — INDEX (multi-session lookup)
- `refresh_tokens.token_hash` — UNIQUE (fast lookup)
- `refresh_tokens.session_id` — INDEX (revoke by session)
- `api_keys.key_prefix` — INDEX (fast lookup)
- `verifications.user_id` — INDEX
- `password_resets.token_hash` — UNIQUE

---

## main.py Integration

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
from components.email.EmailService import emailService
from components.email.EmailTemplateEngine import emailTemplateEngine
from components.health.HealthCheck import healthCheck
from components.health.ReadinessGate import readinessGate
from components.middleware.MiddlewareRegistry import register_middlewares
from components.exceptions.ExceptionHandler import register_exception_handlers
from src.infrastructure.grpc.AuthGrpcServer import authGrpcServer

config = settings()
logger = loggerFactory.create("main", level=config.log_level)
sys_log = loggingSystem(config.app_name)

pg = postgresEngine(config)
redis = redisEngine(config)
http = httpClientFactory(config, logger)
template_engine = emailTemplateEngine(config.email_templates_dir)
email = emailService(config, logger, template_engine)
health = healthCheck(config, pg, redis, http)
grpc_server = authGrpcServer(config, pg, redis)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    sys_log.startup("initializing auth-service engines")
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

    await grpc_server.start()
    sys_log.startup(f"gRPC server started on port {config.grpc_port}")
    sys_log.startup("auth-service ready, accepting traffic")

    yield

    await grpc_server.stop()
    await http.close()
    await pg.close()
    await redis.close()
    sys_log.shutdown("auth-service shutdown complete")


app = FastAPI(title=config.app_name, debug=config.debug, lifespan=lifespan)

register_exception_handlers(app)
register_middlewares(app, config)
app.include_router(health.router)

# v1 routers
from src.infrastructure.routers.v1.AuthRouter import router as auth_router
from src.infrastructure.routers.v1.SessionRouter import router as session_router
from src.infrastructure.routers.v1.TokenRouter import router as token_router
from src.infrastructure.routers.v1.VerificationRouter import router as verification_router

app.include_router(auth_router)
app.include_router(session_router)
app.include_router(token_router)
app.include_router(verification_router)
```

---

## Urutan Implementasi (Recommended)

| Phase | Scope | Detail |
|-------|-------|--------|
| 1 | **Domain** | BaseModel -> Enums -> UserModel -> SessionModel -> RefreshTokenModel -> VerificationModel -> PasswordResetModel -> ApiKeyModel -> Settings -> TokenPayload |
| 2 | **Schemas** | BaseSchema (dari components) -> AuthSchema -> SessionSchema -> TokenSchema -> VerificationSchema -> ApiKeySchema |
| 3 | **Interfaces** | Semua repository interfaces + UoW interface |
| 4 | **Repositories** | Semua concrete repository implementations |
| 5 | **UoW** | PostgresUnitOfWork |
| 6 | **Alembic** | Setup alembic.ini + env.py -> initial migration (semua tables) -> test upgrade/downgrade |
| 7 | **Services** | AuthService -> SessionService -> TokenService (incl. JWT blacklist) -> VerificationService -> ApiKeyService |
| 8 | **Routers** | AuthRouter -> SessionRouter -> TokenRouter -> VerificationRouter |
| 9 | **gRPC** | Proto -> Servicer -> Server |
| 10 | **Integration** | main.py -> Dependencies.py -> middleware (incl. CSRF) + exception handler registration |
| 11 | **Docker** | Dockerfile + docker-compose.yml (dev, incl. migrate service) |
| 12 | **Testing** | Per-fitur: register flow, login flow, session management, token refresh + blacklist, password reset, API key, CSRF |

> Phase 1-5 bisa dikerjakan tanpa running server. Phase 6 butuh database running. Phase 7-8 butuh database + Redis. Phase 9 butuh gRPC setup. Phase 12 setelah semua fitur final.

---

## Crypto Strategy (Benchmark-Based)

Based on performance benchmarks comparing Python libraries vs Rust `k_crypto` module:

### Benchmark Results

| Operation | Python | Rust k_crypto | Winner | Speedup |
|-----------|--------|---------------|--------|---------|
| Argon2id hash | 93 ms | 191 ms | **Python** (argon2-cffi) | 2x |
| BLAKE3 hash | 2.1 µs | 1.6 µs | **Rust** | 1.35x |
| SHA3-256 hash | 4.5 µs | 5.0 µs | Python (negligible) | - |
| AES-256-GCM encrypt | 120 µs | 2.2 µs | **Rust** | 55x |
| AES-256-GCM decrypt | 112 µs | 2.3 µs | **Rust** | 49x |

### Implementation Decision

| Use Case | Implementation | Library | Reason |
|----------|----------------|---------|--------|
| **Password hashing** | Python | `argon2-cffi` | 2x faster than Rust module |
| **Token hashing** (refresh, API key, verification) | Rust | `k_crypto.hash_blake3()` | 1.35x faster, constant time |
| **Data encryption** (sensitive fields) | Rust | `k_crypto.encrypt_aes_gcm()` | 55x faster + AAD support |
| **Data decryption** | Rust | `k_crypto.decrypt_aes_gcm()` | 49x faster + context binding |

### CryptoFactory Hybrid Pattern

```python
# components/crypto/CryptoFactory.py

class cryptoFactory:
    def hash_password(self, password: str) -> str:
        # Use Python argon2-cffi (2x faster)
        return argon2_hasher.hash(password)

    def verify_password(self, password: str, hash: str) -> bool:
        # Use Python argon2-cffi
        return argon2_hasher.verify(hash, password)

    def hash_data(self, data: str) -> str:
        # Use Rust k_crypto BLAKE3 (1.35x faster)
        return k_crypto.hash_blake3(data)

    def encrypt(self, plaintext: str, context: str | None = None) -> EncryptedData:
        # Use Rust k_crypto AES-256-GCM (55x faster + AAD)
        return k_crypto.encrypt_aes_gcm(plaintext, aad=context)

    def decrypt(self, encrypted: EncryptedData, context: str | None = None) -> str:
        # Use Rust k_crypto AES-256-GCM (49x faster + AAD)
        return k_crypto.decrypt_aes_gcm(encrypted, aad=context)
```

### Context-Binding Encryption (AAD)

Rust module supports Additional Authenticated Data (AAD) for context-binding:

```python
# Bind encrypted token to user_id — prevents token theft across users
encrypted = crypto.encrypt(refresh_token, context=f"user:{user_id}")

# Decryption FAILS if context doesn't match (tampering detected)
decrypted = crypto.decrypt(encrypted, context=f"user:{user_id}")
```

**Use AAD for**:
- Refresh tokens (bind to user_id + session_id)
- API keys (bind to service_name)
- Encrypted sensitive user data (bind to user_id)

---

## Security Checklist

- [ ] Password di-hash pakai Argon2id (via Python argon2-cffi — 2x faster)
- [ ] Refresh token di-hash di DB (bukan plaintext)
- [ ] API key di-hash di DB, plaintext ditampilkan SEKALI saat create
- [ ] Verification code di-hash di DB
- [ ] Password reset token di-hash di DB
- [ ] Session ID di Redis punya TTL
- [ ] Token rotation pada refresh (old revoked, new generated)
- [ ] JWT blacklist di Redis — logout, password change, suspend invalidate access token
- [ ] JWT payload include `jti` untuk individual blacklist
- [ ] CSRF token set saat login, validated di setiap state-changing request (session-based)
- [ ] CSRF cookie HttpOnly=False (supaya frontend bisa baca), tapi Secure + SameSite=Lax
- [ ] Reset password revoke semua session + blacklist semua access tokens
- [ ] Rate limit pada login endpoint
- [ ] Response field obfuscation pada semua schema
- [ ] Sensitive data di body (POST), bukan query param
- [ ] CORS, trusted host, blacklist, CSRF middleware aktif
- [ ] Semua error di-log (no silent error)
- [ ] gRPC untuk internal only, HTTP untuk external
- [ ] SMTP credentials dari ENV, TIDAK hardcode
- [ ] Email sending di background task, TIDAK block auth response
- [ ] Email failure TIDAK block auth flow (log error, return False)
- [ ] Alembic migration dijalankan di CI/CD sebelum deploy, BUKAN di app startup
- [ ] Migration harus reversible (downgrade function)