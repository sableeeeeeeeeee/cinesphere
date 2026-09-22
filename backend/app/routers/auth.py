from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import User
from app.schemas import (
    UserCreate,
    LoginRequest,
    TokenResponse
)

from app.security import (
    hash_password,
    verify_password,
    create_access_token
)


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post(
    "/register",
    response_model=TokenResponse
)
async def register(
    data: UserCreate,
    db: AsyncSession =
        Depends(get_db)
):

    existing = await db.scalar(
        select(User).where(
            User.email ==
            data.email.lower()
        )
    )

    if existing:

        raise HTTPException(
            400,
            "Email already registered"
        )

    user = User(
        name=data.name,
        email=data.email.lower(),
        password_hash=hash_password(
            data.password
        )
    )

    db.add(user)

    await db.commit()

    await db.refresh(user)

    return TokenResponse(
        access_token=create_access_token(
            user.id,
            user.is_admin
        )
    )


@router.post(
    "/login",
    response_model=TokenResponse
)
async def login(
    data: LoginRequest,
    db: AsyncSession =
        Depends(get_db)
):

    user = await db.scalar(
        select(User).where(
            User.email ==
            data.email.lower()
        )
    )

    if (
        not user
        or not verify_password(
            data.password,
            user.password_hash
        )
    ):

        raise HTTPException(
            401,
            "Invalid email or password"
        )

    return TokenResponse(
        access_token=create_access_token(
            user.id,
            user.is_admin
        )
    )