from __future__ import annotations

from enum import Enum


class hashAlgorithm(Enum):
    ARGON2ID = "argon2id"
    BLAKE3 = "blake3"
    SHA3_256 = "sha3_256"


class encryptAlgorithm(Enum):
    AES256GCM = "aes256gcm"
    CHACHA20_POLY1305 = "chacha20poly1305"


class signAlgorithm(Enum):
    HMAC_SHA256 = "hmac_sha256"
    ED25519 = "ed25519"
