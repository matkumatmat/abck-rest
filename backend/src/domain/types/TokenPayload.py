from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class tokenPayload:
    sub: str
    sid: str
    jti: str
    exp: int
    iat: int
    typ: str

    def to_dict(self) -> dict:
        return {
            "sub": self.sub,
            "sid": self.sid,
            "jti": self.jti,
            "exp": self.exp,
            "iat": self.iat,
            "typ": self.typ,
        }

    @classmethod
    def from_dict(cls, data: dict) -> tokenPayload:
        return cls(
            sub=data["sub"],
            sid=data["sid"],
            jti=data["jti"],
            exp=data["exp"],
            iat=data["iat"],
            typ=data["typ"],
        )
