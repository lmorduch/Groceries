# ABOUTME: Symmetric encryption helpers for sensitive fields stored in the database
# ABOUTME: Uses Fernet (AES-128-CBC + HMAC-SHA256); requires FIELD_ENCRYPTION_KEY env var

import os

from cryptography.fernet import Fernet


def _fernet() -> Fernet:
    key = os.environ.get("FIELD_ENCRYPTION_KEY")
    if not key:
        raise RuntimeError(
            "FIELD_ENCRYPTION_KEY is not set. "
            "Generate one with: python -c \"from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())\""
        )
    return Fernet(key.encode())


def encrypt(value: str) -> str:
    return _fernet().encrypt(value.encode()).decode()


def decrypt(value: str) -> str:
    return _fernet().decrypt(value.encode()).decode()
