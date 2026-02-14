from __future__ import annotations

from pydantic import EmailStr, Field

from components.schemas.BaseResponse import baseRequest, baseResponse


class registerRequest(baseRequest):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    name: str = Field(min_length=1, max_length=100)


class loginRequest(baseRequest):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class authResponse(baseResponse):
    at: str = Field(alias="_at")
    rt: str = Field(alias="_rt")
    exp: int = Field(alias="_exp")


class registerResponse(baseResponse):
    uid: str = Field(alias="_uid")
    em: str = Field(alias="_em")
    st: str = Field(alias="_st")
