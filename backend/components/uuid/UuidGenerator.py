from __future__ import annotations

from datetime import datetime, timezone

from uuid_utils import uuid7


class uuidGenerator:

    @staticmethod
    def create() -> str:
        return str(uuid7())

    @staticmethod
    def create_hex() -> str:
        return uuid7().hex

    @staticmethod
    def create_bytes() -> bytes:
        return uuid7().bytes

    @staticmethod
    def create_prefixed(prefix: str) -> str:
        return f"{prefix}_{uuid7()}"

    @staticmethod
    def is_valid(value: str) -> bool:
        if not value:
            return False
        clean = value.split("_")[-1] if "_" in value else value
        if len(clean) != 36:
            return False
        try:
            parts = clean.split("-")
            if len(parts) != 5:
                return False
            lengths = [8, 4, 4, 4, 12]
            for part, expected_len in zip(parts, lengths, strict=False):
                if len(part) != expected_len:
                    return False
                int(part, 16)
            return True
        except ValueError:
            return False

    @staticmethod
    def extract_timestamp(uuid7_str: str) -> datetime | None:
        try:
            clean = uuid7_str.split("_")[-1] if "_" in uuid7_str else uuid7_str
            hex_str = clean.replace("-", "")
            timestamp_ms = int(hex_str[:12], 16)
            return datetime.fromtimestamp(timestamp_ms / 1000, tz=timezone.utc)
        except (ValueError, OSError):
            return None
