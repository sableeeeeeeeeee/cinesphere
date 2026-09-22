from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Movie
from app.schemas import MovieResponse


router = APIRouter(
    prefix="/movies",
    tags=["Movies"]
)


@router.get(
    "",
    response_model=list[MovieResponse]
)
async def get_movies(
    db: AsyncSession =
        Depends(get_db)
):

    result = await db.scalars(
        select(Movie)
        .order_by(Movie.created_at.desc())
    )

    return list(result.all())


@router.get(
    "/{movie_id}",
    response_model=MovieResponse
)
async def get_movie(
    movie_id: str,
    db: AsyncSession =
        Depends(get_db)
):

    movie = await db.get(
        Movie,
        movie_id
    )

    if not movie:

        raise HTTPException(
            404,
            "Movie not found"
        )

    return movie