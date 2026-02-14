from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Request

from components.decorators.AccessTokenDecorator import BearerToken, require_access_token
from components.schemas.BaseResponse import successResponse
from src.application.schemas.SessionSchema import sessionItemResponse, sessionListResponse
from src.application.services.SessionService import sessionService
from src.application.services.TokenService import tokenService

router = APIRouter(prefix="/v1/sessions", tags=["sessions"])


def get_session_service() -> sessionService:
    from src.Dependencies import get_session_service as _get_session_service

    return _get_session_service()


def get_token_service() -> tokenService:
    from src.Dependencies import get_token_service as _get_token_service

    return _get_token_service()


@router.get("")
@require_access_token
async def list_sessions(
    request: Request,
    session_service: Annotated[sessionService, Depends(get_session_service)],
    token_service: Annotated[tokenService, Depends(get_token_service)],
    _: BearerToken = None,
    access_token: str = "",
) -> successResponse:
    payload = await token_service.validate_access(access_token)

    sessions = await session_service.list_sessions(payload.sub)

    items = [
        sessionItemResponse(
            sid=s.id,
            ip=s.ip_address,
            ua=s.user_agent,
            la=s.last_activity,
            ca=s.created_at,
        )
        for s in sessions
    ]

    response_data = sessionListResponse(
        sessions=items,
        total=len(items),
    )

    return successResponse(data=response_data.model_dump(by_alias=True))


@router.delete("/{session_id}")
@require_access_token
async def revoke_session(
    request: Request,
    session_id: str,
    session_service: Annotated[sessionService, Depends(get_session_service)],
    token_service: Annotated[tokenService, Depends(get_token_service)],
    _: BearerToken = None,
    access_token: str = "",
) -> successResponse:
    payload = await token_service.validate_access(access_token)

    await session_service.revoke_session(payload.sub, session_id)

    return successResponse(data={"message": "Session revoked successfully"})


@router.delete("")
@require_access_token
async def revoke_all_sessions(
    request: Request,
    session_service: Annotated[sessionService, Depends(get_session_service)],
    token_service: Annotated[tokenService, Depends(get_token_service)],
    _: BearerToken = None,
    access_token: str = "",
) -> successResponse:
    payload = await token_service.validate_access(access_token)

    count = await session_service.revoke_all_sessions(payload.sub)

    return successResponse(data={"message": f"{count} sessions revoked"})
