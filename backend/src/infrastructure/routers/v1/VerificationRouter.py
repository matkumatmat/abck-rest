from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, Query, Request

from components.decorators.AccessTokenDecorator import BearerToken, require_access_token
from components.schemas.BaseResponse import successResponse
from src.application.schemas.VerificationSchema import (
    forgotPasswordRequest,
    resetPasswordRequest,
    verificationResponse,
)
from src.application.services.TokenService import tokenService
from src.application.services.VerificationService import verificationService

router = APIRouter(prefix="/v1", tags=["verification"])


def get_verification_service() -> verificationService:
    from src.Dependencies import get_verification_service as _get_verification_service

    return _get_verification_service()


def get_token_service() -> tokenService:
    from src.Dependencies import get_token_service as _get_token_service

    return _get_token_service()


@router.get("/verify-email")
async def verify_email(
    background_tasks: BackgroundTasks,
    verification_service: Annotated[verificationService, Depends(get_verification_service)],
    token: str = Query(..., description="Verification token from email"),
) -> successResponse:
    await verification_service.verify_email(
        token=token,
        background_tasks=background_tasks,
    )

    response_data = verificationResponse(
        success=True,
        m="Email verified successfully",
    )

    return successResponse(data=response_data.model_dump(by_alias=True))


@router.post("/resend-verification")
@require_access_token
async def resend_verification(
    request: Request,
    background_tasks: BackgroundTasks,
    verification_service: Annotated[verificationService, Depends(get_verification_service)],
    token_service: Annotated[tokenService, Depends(get_token_service)],
    _: BearerToken = None,
    access_token: str = "",
) -> successResponse:
    payload = await token_service.validate_access(access_token)

    await verification_service.create_email_verification(
        user_id=payload.sub,
        background_tasks=background_tasks,
    )

    response_data = verificationResponse(
        success=True,
        m="Verification email sent",
    )

    return successResponse(data=response_data.model_dump(by_alias=True))


@router.post("/forgot-password")
async def forgot_password(
    data: forgotPasswordRequest,
    background_tasks: BackgroundTasks,
    verification_service: Annotated[verificationService, Depends(get_verification_service)],
) -> successResponse:
    await verification_service.create_password_reset(
        email=data.email,
        background_tasks=background_tasks,
    )

    response_data = verificationResponse(
        success=True,
        m="If the email exists, a reset link has been sent",
    )

    return successResponse(data=response_data.model_dump(by_alias=True))


@router.post("/reset-password")
async def reset_password(
    data: resetPasswordRequest,
    verification_service: Annotated[verificationService, Depends(get_verification_service)],
) -> successResponse:
    await verification_service.reset_password(
        token=data.token,
        new_password=data.new_password,
    )

    response_data = verificationResponse(
        success=True,
        m="Password reset successfully",
    )

    return successResponse(data=response_data.model_dump(by_alias=True))
