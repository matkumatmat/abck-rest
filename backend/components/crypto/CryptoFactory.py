from __future__ import annotations

import os
from dataclasses import dataclass
from typing import TYPE_CHECKING

import k_crypto

if TYPE_CHECKING:
    from components.config.ComponentSettings import componentSettings


@dataclass
class EncryptedData:
    ciphertext: bytes
    nonce: bytes
    algorithm: str

    def to_dict(self) -> dict:
        return {
            "ciphertext": self.ciphertext.hex(),
            "nonce": self.nonce.hex(),
            "algorithm": self.algorithm,
        }

    @classmethod
    def from_dict(cls, data: dict) -> EncryptedData:
        return cls(
            ciphertext=bytes.fromhex(data["ciphertext"]),
            nonce=bytes.fromhex(data["nonce"]),
            algorithm=data["algorithm"],
        )


class cryptoFactory:

    def __init__(self, config: componentSettings | None = None) -> None:
        self._config = config
        self._default_hash = "argon2id"
        self._default_encrypt = "aes256gcm"
        self._argon_memory = 65536
        self._argon_iterations = 3
        self._argon_parallelism = 4

        if config:
            self._default_hash = config.crypto_default_hash
            self._default_encrypt = config.crypto_default_encrypt
            self._argon_memory = config.crypto_argon_memory
            self._argon_iterations = config.crypto_argon_iterations
            self._argon_parallelism = config.crypto_argon_parallelism

    # =========================================================================
    # PASSWORD HASHING (Argon2id)
    # =========================================================================

    def hash_password(
        self,
        password: str,
        memory_cost: int | None = None,
        time_cost: int | None = None,
        parallelism: int | None = None,
        salt: bytes | None = None,
    ) -> str:
        return k_crypto.hash_password(
            password,
            memory_cost or self._argon_memory,
            time_cost or self._argon_iterations,
            parallelism or self._argon_parallelism,
            list(salt) if salt else None,
        )

    def verify_password(self, password: str, hashed: str) -> bool:
        return k_crypto.verify_password(password, hashed)

    # =========================================================================
    # DATA HASHING (BLAKE3, SHA3)
    # =========================================================================

    def hash_data(self, data: str | bytes, algorithm: str = "blake3") -> bytes:
        if isinstance(data, str):
            data = data.encode()
        return bytes(k_crypto.hash_data(data, algorithm))

    def hash_data_hex(self, data: str | bytes, algorithm: str = "blake3") -> str:
        if isinstance(data, str):
            data = data.encode()
        return k_crypto.hash_data_hex(data, algorithm)

    # =========================================================================
    # ENCRYPTION (AES-256-GCM, ChaCha20-Poly1305)
    # =========================================================================

    def encrypt(
        self,
        plaintext: str | bytes,
        key: bytes | None = None,
        aad: str | bytes | None = None,
        algorithm: str | None = None,
    ) -> EncryptedData:
        if isinstance(plaintext, str):
            plaintext = plaintext.encode()

        if key is None:
            key = self._get_master_key()

        if isinstance(aad, str):
            aad = aad.encode()

        algorithm = algorithm or self._default_encrypt

        ciphertext, nonce = k_crypto.encrypt(
            plaintext,
            key,
            aad,
            algorithm,
        )

        return EncryptedData(
            ciphertext=bytes(ciphertext),
            nonce=bytes(nonce),
            algorithm=algorithm,
        )

    def decrypt(
        self,
        encrypted: EncryptedData | dict,
        key: bytes | None = None,
        aad: str | bytes | None = None,
    ) -> bytes:
        if isinstance(encrypted, dict):
            encrypted = EncryptedData.from_dict(encrypted)

        if key is None:
            key = self._get_master_key()

        if isinstance(aad, str):
            aad = aad.encode()

        return bytes(
            k_crypto.decrypt(
                encrypted.ciphertext,
                key,
                encrypted.nonce,
                aad,
                encrypted.algorithm,
            )
        )

    def decrypt_to_str(
        self,
        encrypted: EncryptedData | dict,
        key: bytes | None = None,
        aad: str | bytes | None = None,
    ) -> str:
        return self.decrypt(encrypted, key, aad).decode()

    # =========================================================================
    # SIGNING (HMAC-SHA256, Ed25519)
    # =========================================================================

    def sign(
        self,
        data: str | bytes,
        key: bytes | None = None,
        algorithm: str = "hmac_sha256",
    ) -> bytes:
        if isinstance(data, str):
            data = data.encode()

        if key is None:
            key = self._get_master_key()

        return bytes(k_crypto.sign(data, key, algorithm))

    def sign_hex(
        self,
        data: str | bytes,
        key: bytes | None = None,
        algorithm: str = "hmac_sha256",
    ) -> str:
        return self.sign(data, key, algorithm).hex()

    def verify_signature(
        self,
        data: str | bytes,
        signature: bytes | str,
        key: bytes | None = None,
        algorithm: str = "hmac_sha256",
    ) -> bool:
        if isinstance(data, str):
            data = data.encode()

        if isinstance(signature, str):
            signature = bytes.fromhex(signature)

        if key is None:
            key = self._get_master_key()

        return k_crypto.verify_signature(data, signature, key, algorithm)

    # =========================================================================
    # KEY GENERATION
    # =========================================================================

    @staticmethod
    def generate_key(length: int = 32) -> bytes:
        return bytes(k_crypto.generate_key(length))

    @staticmethod
    def generate_salt(length: int = 16) -> bytes:
        return bytes(k_crypto.generate_salt(length))

    @staticmethod
    def generate_keypair_ed25519() -> tuple[bytes, bytes]:
        private_key, public_key = k_crypto.generate_keypair_ed25519()
        return bytes(private_key), bytes(public_key)

    # =========================================================================
    # INTERNAL
    # =========================================================================

    def _get_master_key(self) -> bytes:
        key_env = self._config.crypto_master_key if self._config else os.environ.get("CRYPTO_MASTER_KEY")
        if not key_env:
            raise ValueError("CRYPTO_MASTER_KEY not set in config or environment")

        key_bytes = bytes.fromhex(key_env) if len(key_env) == 64 else key_env.encode()

        if len(key_bytes) != 32:
            raise ValueError("CRYPTO_MASTER_KEY must be 32 bytes (64 hex chars or 32 char string)")

        return key_bytes


crypto = cryptoFactory()
