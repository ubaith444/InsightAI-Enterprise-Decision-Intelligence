import base64
import hashlib

from cryptography.fernet import Fernet, InvalidToken

from app.core.config import get_settings

PREFIX = "enc::"


def _fernet() -> Fernet:
    digest = hashlib.sha256(get_settings().secret_key.encode("utf-8")).digest()
    return Fernet(base64.urlsafe_b64encode(digest))


def encrypt_secret(value: str) -> str:
    if not value or value.startswith(PREFIX):
        return value
    return f"{PREFIX}{_fernet().encrypt(value.encode('utf-8')).decode('utf-8')}"


def decrypt_secret(value: str) -> str:
    if not value or not value.startswith(PREFIX):
        return value
    try:
        return _fernet().decrypt(value.removeprefix(PREFIX).encode("utf-8")).decode("utf-8")
    except InvalidToken:
        return value


def mask_secret(value: str) -> str:
    plain = decrypt_secret(value)
    if "://" not in plain:
        return "***"
    scheme, rest = plain.split("://", 1)
    if "@" in rest:
        host = rest.split("@", 1)[1]
        return f"{scheme}://***:***@{host}"
    return f"{scheme}://***"
