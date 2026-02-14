from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends

from components.schemas.BaseResponse import successResponse
from src.application.schemas.TokenSchema import refreshTokenRequest, tokenResponse
from src.application.services.TokenService import tokenService

router = APIRouter(prefix="/v1/token", tags=["token"])


def get_token_service() -> tokenService:
    from src.Dependencies import get_token_service as _get_token_service

    return _get_token_service()


@router.post("/refresh")
async def refresh_token(
    data: refreshTokenRequest,
    token_service: Annotated[tokenService, Depends(get_token_service)],
) -> successResponse:
    access_token, refresh_token, expires_in = await token_service.refresh(data.refresh_token)

    response_data = tokenResponse(
        at=access_token,
        rt=refresh_token,
        exp=expires_in,
    )

    return successResponse(data=response_data.model_dump(by_alias=True))
