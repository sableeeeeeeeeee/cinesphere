from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from sqlalchemy import select

from sqlalchemy.orm import (
    selectinload
)

from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db

from app.models import (
    Showtime,
    Seat,
    BookingSeat
)

from app.schemas import (
    ShowtimeResponse,
    SeatResponse,
    LockSeatsRequest,
    LockSeatsResponse
)

from app.services.seat_lock import (
    lock_seats,
    LOCK_SECONDS
)


router = APIRouter(
    prefix="/showtimes",
    tags=["Showtimes"]
)


@router.get(
    "",
    response_model=list[ShowtimeResponse]
)
async def get_showtimes(
    movie_id: str | None = None,
    db: AsyncSession =
        Depends(get_db)
):

    statement = (
        select(Showtime)
        .options(
            selectinload(
                Showtime.screen
            )
        )
        .order_by(
            Showtime.show_date,
            Showtime.show_time
        )
    )

    if movie_id:

        statement = statement.where(
            Showtime.movie_id == movie_id
        )

    rows = (
        await db.scalars(
            statement
        )
    ).all()

    return [
        ShowtimeResponse(
            id=x.id,
            movie_id=x.movie_id,
            screen_id=x.screen_id,
            show_date=x.show_date,
            show_time=x.show_time,
            screen_number=x.screen.screen_number
        )
        for x in rows
    ]


@router.get(
    "/{showtime_id}/seats",
    response_model=list[SeatResponse]
)
async def get_seats(
    showtime_id: int,
    db: AsyncSession =
        Depends(get_db)
):

    showtime = await db.get(
        Showtime,
        showtime_id
    )

    if not showtime:

        raise HTTPException(
            404,
            "Showtime not found"
        )

    seats = (
        await db.scalars(
            select(Seat)
            .where(
                Seat.screen_id ==
                showtime.screen_id
            )
            .order_by(Seat.id)
        )
    ).all()

    booked_ids = set(
        (
            await db.scalars(
                select(
                    BookingSeat.seat_id
                )
                .join(
                    BookingSeat.booking
                )
                .where(
                    BookingSeat.booking.has(
                        showtime_id=showtime_id
                    ),
                    BookingSeat.booking.has(
                        status="confirmed"
                    )
                )
            )
        ).all()
    )

    from app.redis_client import redis
    from app.services.seat_lock import lock_key

    result = []

    for seat in seats:

        if seat.id in booked_ids:

            status = "booked"

        elif await redis.exists(
            lock_key(
                showtime_id,
                seat.id
            )
        ):

            status = "locked"

        else:

            status = "available"

        result.append(
            SeatResponse(
                id=seat.id,
                seat_number=seat.seat_number,
                row_name=seat.row_name,
                tier=seat.tier,
                price=seat.price,
                status=status
            )
        )

    return result


@router.post(
    "/{showtime_id}/lock-seats",
    response_model=LockSeatsResponse
)
async def lock_showtime_seats(
    showtime_id: int,
    data: LockSeatsRequest,
    db: AsyncSession =
        Depends(get_db)
):

    showtime = await db.get(
        Showtime,
        showtime_id
    )

    if not showtime:

        raise HTTPException(
            404,
            "Showtime not found"
        )

    seat_ids = list(
        dict.fromkeys(
            data.seat_ids
        )
    )

    seats = (
        await db.scalars(
            select(Seat)
            .where(
                Seat.id.in_(seat_ids),
                Seat.screen_id ==
                showtime.screen_id
            )
        )
    ).all()

    if len(seats) != len(seat_ids):

        raise HTTPException(
            400,
            "One or more seats are invalid"
        )

    token = await lock_seats(
        showtime_id,
        seat_ids
    )

    if not token:

        raise HTTPException(
            409,
            "One or more seats are currently locked"
        )

    return LockSeatsResponse(
        token=token,
        expires_in=LOCK_SECONDS,
        seat_ids=seat_ids
    )