from __future__ import annotations

from enum import StrEnum


class apiKeyStatusEnum(StrEnum):
    ACTIVE = "ACTIVE"
    REVOKED = "REVOKED"
    EXPIRED = "EXPIRED"
