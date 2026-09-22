import hashlib
import hmac
import os

from datetime import datetime, timedelta, timezone

from jose import jwt


ALGORITHM = "HS256"

SECRET_KEY = os.getenv(
    "SECRET_KEY",
    "dev-secret-change-me"
)

EXPIRE_MINUTES = int(
    os.getenv(
        "ACCESS_TOKEN_EXPIRE_MINUTES",
        "120"
    )
)


def hash_password(password: str) -> str:

    salt = os.urandom(16)

    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode(),
        salt,
        200_000
    )

    return (
        salt.hex()
        + ":"
        + digest.hex()
    )


def verify_password(
    password: str,
    stored: str
) -> bool:

    try:

        salt_hex, digest_hex = stored.split(
            ":",
            1
        )

        salt = bytes.fromhex(
            salt_hex
        )

        digest = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode(),
            salt,
            200_000
        )

        return hmac.compare_digest(
            digest.hex(),
            digest_hex
        )

    except ValueError:

        return False


def create_access_token(
    user_id: int,
    is_admin: bool
) -> str:

    expiration = (
        datetime.now(timezone.utc)
        + timedelta(
            minutes=EXPIRE_MINUTES
        )
    )

    payload = {
        "sub": str(user_id),
        "is_admin": is_admin,
        "exp": expiration
    }

    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )