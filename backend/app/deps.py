import os

from fastapi import (
    Depends,
    HTTPException,
    status
)

from fastapi.security import (
    HTTPBearer,
    HTTPAuthorizationCredentials
)

from jose import jwt, JWTError

from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import User


security = HTTPBearer(
    auto_error=False
)

SECRET_KEY = os.getenv(
    "SECRET_KEY",
    "dev-secret-change-me"
)

ALGORITHM = "HS256"


async def get_current_user(
    credentials: HTTPAuthorizationCredentials =
        Depends(security),
    db: AsyncSession =
        Depends(get_db)
):

    if not credentials:

        raise HTTPException(
            status_code=401,
            detail="Login required"
        )

    try:

        payload = jwt.decode(
            credentials.credentials,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        user_id = int(
            payload["sub"]
        )

    except (
        JWTError,
        KeyError,
        ValueError
    ):

        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )

    user = await db.get(
        User,
        user_id
    )

    if not user:

        raise HTTPException(
            status_code=401,
            detail="User not found"
        )

    return user


async def require_admin(
    user: User =
        Depends(get_current_user)
):

    if not user.is_admin:

        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )

    return user