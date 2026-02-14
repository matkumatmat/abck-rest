from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Cookie, Depends, Request, Response

from components.decorators.AccessTokenDecorator import BearerToken, require_access_token
from components.schemas.BaseResponse import successResponse
from src.application.schemas.AuthSchema import (
    authResponse,
    loginRequest,
    registerRequest,
    registerResponse,
)
from src.application.services.AuthService import authService
from src.application.services.TokenService import tokenService
from src.domain.config.Settings import settings

router = APIRouter(prefix="/v1/auth", tags=["auth"])


def get_auth_service() -> authService:
    from src.Dependencies import get_auth_service as _get_auth_service

    return _get_auth_service()


def get_token_service() -> tokenService:
    from src.Dependencies import get_token_service as _get_token_service

    return _get_token_service()


def get_settings() -> settings:
    from src.Dependencies import get_settings as _get_settings

    return _get_settings()


@router.post("/register")
async def register(
    data: registerRequest,
    background_tasks: BackgroundTasks,
    auth_service: Annotated[authService, Depends(get_auth_service)],
) -> successResponse:
    user = await auth_service.register(
        email=data.email,
        password=data.password,
        name=data.name,
        background_tasks=background_tasks,
    )

    response_data = registerResponse(
        uid=user.id,
        em=user.email,
        st=user.status.value,
    )

    return successResponse(data=response_data.model_dump(by_alias=True))


@router.post("/login")
async def login(
    request: Request,
    response: Response,
    data: loginRequest,
    auth_service: Annotated[authService, Depends(get_auth_service)],
    config: Annotated[settings, Depends(get_settings)],
) -> successResponse:
    ip_address = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("User-Agent", "unknown")

    access_token, refresh_token, expires_in, csrf_token = await auth_service.login(
        email=data.email,
        password=data.password,
        ip_address=ip_address,
        user_agent=user_agent,
    )

    response.set_cookie(
        key=config.csrf_cookie_name,
        value=csrf_token,
        httponly=False,
        secure=config.session_cookie_secure,
        samesite=config.session_cookie_samesite,
        max_age=config.session_expires,
    )

    response_data = authResponse(
        at=access_token,
        rt=refresh_token,
        exp=expires_in,
    )

    return successResponse(data=response_data.model_dump(by_alias=True))


@router.post("/logout")
@require_access_token
async def logout(
    request: Request,
    response: Response,
    auth_service: Annotated[authService, Depends(get_auth_service)],
    token_service: Annotated[tokenService, Depends(get_token_service)],
    config: Annotated[settings, Depends(get_settings)],
    _: BearerToken = None,
    access_token: str = "",
) -> successResponse:
    payload = await token_service.validate_access(access_token)

    await auth_service.logout(
        session_id=payload.sid,
        access_jti=payload.jti,
        access_exp=payload.exp,
    )

    response.delete_cookie(key=config.csrf_cookie_name)

    return successResponse(data={"message": "Logged out successfully"})
