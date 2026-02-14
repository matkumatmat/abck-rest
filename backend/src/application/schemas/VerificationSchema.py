from __future__ import annotations

from pydantic import EmailStr, Field

from components.schemas.BaseResponse import baseRequest, baseResponse


class forgotPasswordRequest(baseRequest):
    email: EmailStr


class resetPasswordRequest(baseRequest):
    token: str = Field(min_length=1)
    new_password: str = Field(min_length=8, max_length=128)


class verificationResponse(baseResponse):
    success: bool
    m: str = Field(alias="_m")
