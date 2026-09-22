import re

from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from sqlalchemy import (
    select,
    func
)

from sqlalchemy.orm import selectinload

from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db

from app.models import (
    Movie,
    Screen,
    Showtime,
    Booking
)

from app.schemas import (
    MovieCreate,
    MovieResponse,
    ShowtimeCreate,
    ShowtimeResponse
)

from app.deps import require_admin


router = APIRouter(
    prefix="/admin",
    tags=["Admin"]
)


def slugify(text: str):

    text = text.lower()

    text = re.sub(
        r"[^a-z0-9]+",
        "-",
        text
    )

    return text.strip("-")


@router.post(
    "/movies",
    response_model=MovieResponse
)
async def create_movie(
    data: MovieCreate,
    db: AsyncSession =
        Depends(get_db),
    _: object =
        Depends(require_admin)
):

    movie_id = (
        data.id
        or slugify(data.title)
    )

    if await db.get(
        Movie,
        movie_id
    ):

        raise HTTPException(
            409,
            "Movie ID already exists"
        )

    movie = Movie(
        id=movie_id,
        **data.model_dump(
            exclude={"id"}
        )
    )

    db.add(movie)

    await db.commit()

    await db.refresh(movie)

    return movie


@router.put(
    "/movies/{movie_id}",
    response_model=MovieResponse
)
async def update_movie(
    movie_id: str,
    data: MovieCreate,
    db: AsyncSession =
        Depends(get_db),
    _: object =
        Depends(require_admin)
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

    values = data.model_dump(
        exclude={"id"}
    )

    for key, value in values.items():

        setattr(
            movie,
            key,
            value
        )

    await db.commit()

    await db.refresh(movie)

    return movie


@router.delete(
    "/movies/{movie_id}"
)
async def delete_movie(
    movie_id: str,
    db: AsyncSession =
        Depends(get_db),
    _: object =
        Depends(require_admin)
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

    await db.delete(movie)

    await db.commit()

    return {
        "message":
            "Movie deleted"
    }


@router.get("/screens")
async def get_screens(
    db: AsyncSession =
        Depends(get_db),
    _: object =
        Depends(require_admin)
):

    screens = (
        await db.scalars(
            select(Screen)
            .options(
                selectinload(
                    Screen.seats
                )
            )
            .order_by(
                Screen.screen_number
            )
        )
    ).all()

    return [
        {
            "id": screen.id,
            "screen_number":
                screen.screen_number,
            "name":
                screen.name,
            "seat_count":
                len(screen.seats)
        }

        for screen in screens
    ]


@router.post(
    "/showtimes",
    response_model=ShowtimeResponse
)
async def create_showtime(
    data: ShowtimeCreate,
    db: AsyncSession =
        Depends(get_db),
    _: object =
        Depends(require_admin)
):

    movie = await db.get(
        Movie,
        data.movie_id
    )

    if not movie:

        raise HTTPException(
            404,
            "Movie not found"
        )

    screen = await db.get(
        Screen,
        data.screen_id
    )

    if not screen:

        raise HTTPException(
            404,
            "Screen not found"
        )

    showtime = Showtime(
        **data.model_dump()
    )

    db.add(showtime)

    await db.commit()

    await db.refresh(showtime)

    return ShowtimeResponse(
        id=showtime.id,
        movie_id=
            showtime.movie_id,
        screen_id=
            showtime.screen_id,
        show_date=
            showtime.show_date,
        show_time=
            showtime.show_time,
        screen_number=
            screen.screen_number
    )


@router.get("/dashboard")
async def dashboard(
    db: AsyncSession =
        Depends(get_db),
    _: object =
        Depends(require_admin)
):

    total_movies = await db.scalar(
        select(
            func.count(Movie.id)
        )
    )

    showing = await db.scalar(
        select(
            func.count(Movie.id)
        ).where(
            Movie.status ==
            "showing"
        )
    )

    upcoming = await db.scalar(
        select(
            func.count(Movie.id)
        ).where(
            Movie.status ==
            "upcoming"
        )
    )

    leaving = await db.scalar(
        select(
            func.count(Movie.id)
        ).where(
            Movie.status ==
            "leaving"
        )
    )

    bookings = await db.scalar(
        select(
            func.count(Booking.id)
        )
    )

    revenue = await db.scalar(
        select(
            func.coalesce(
                func.sum(
                    Booking.total_amount
                ),
                0
            )
        ).where(
            Booking.status ==
            "confirmed"
        )
    )

    return {
        "total_movies":
            total_movies,

        "now_showing":
            showing,

        "coming_soon":
            upcoming,

        "leaving_soon":
            leaving,

        "bookings":
            bookings,

        "revenue":
            revenue
    }