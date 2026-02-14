from __future__ import annotations

from enum import StrEnum


class sessionStatusEnum(StrEnum):
    ACTIVE = "ACTIVE"
    EXPIRED = "EXPIRED"
    REVOKED = "REVOKED"
