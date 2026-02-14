from __future__ import annotations

import re

from pydantic import model_validator
from sqlmodel import Field

from src.domain.enums.UserStatusEnum import userStatusEnum
from src.domain.models.BaseModel import baseModel


class userModel(baseModel, table=True):
    __tablename__ = "users"

    email: str = Field(unique=True, index=True, max_length=255)
    password_hash: str = Field(max_length=255)
    name: str = Field(max_length=100)
    status: userStatusEnum = Field(default=userStatusEnum.PENDING_VERIFICATION)

    @model_validator(mode="after")
    def validate_email_format(self) -> userModel:
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(pattern, self.email):
            raise ValueError("Invalid email format")
        return self

    def is_active(self) -> bool:
        return self.status == userStatusEnum.ACTIVE

    def is_verified(self) -> bool:
        return self.status != userStatusEnum.PENDING_VERIFICATION

    def __bool__(self) -> bool:
        return self.is_active()

    def activate(self) -> None:
        if self.status == userStatusEnum.PENDING_VERIFICATION:
            self.status = userStatusEnum.ACTIVE
            self.touch()

    def suspend(self) -> None:
        self.status = userStatusEnum.SUSPENDED
        self.touch()

    def deactivate(self) -> None:
        self.status = userStatusEnum.INACTIVE
        self.touch()

    def update_password(self, new_hash: str) -> None:
        self.password_hash = new_hash
        self.touch()
