from __future__ import annotations

from components.config.ComponentSettings import componentSettings


class settings(componentSettings):
    # -- App --
    app_name: str = "auth-service"
    app_port: int = 8002
    debug: bool = True
    frontend_url: str = "http://localhost:3000"

    # -- JWT --
    jwt_secret: str
    jwt_access_expires: int = 900
    jwt_refresh_expires: int = 604800
    jwt_algorithm: str = "HS256"

    # -- Session --
    session_expires: int = 86400
    session_cookie_name: str = "sid"
    session_cookie_secure: bool = True
    session_cookie_httponly: bool = True
    session_cookie_samesite: str = "lax"
    session_max_per_user: int = 5

    # -- Verification --
    verification_code_length: int = 6
    verification_expires: int = 3600
    password_reset_expires: int = 1800

    # -- API Key --
    api_key_prefix_length: int = 8
    api_key_length: int = 48

    # -- Rate Limit (login specific) --
    login_rate_limit_window: int = 300
    login_rate_limit_max: int = 5

    # -- gRPC --
    grpc_port: int = 50051
