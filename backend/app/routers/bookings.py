import secrets

from decimal import Decimal

from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from sqlalchemy import select

from sqlalchemy.orm import selectinload

from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db

from app.models import (
    Booking,
    BookingSeat,
    BookingFood,
    Seat,
    FoodItem,
    Showtime
)

from app.schemas import (
    BookingCreate,
    BookingResponse
)

from app.services.seat_lock import (
    verify_locks,
    release_locks
)


router = APIRouter(
    prefix="/bookings",
    tags=["Bookings"]
)


def generate_booking_code():

    return (
        "CS-"
        + secrets.token_hex(4).upper()
    )


@router.post(
    "",
    response_model=BookingResponse
)
async def create_booking(
    data: BookingCreate,
    db: AsyncSession =
        Depends(get_db)
):

    showtime = await db.scalar(
        select(Showtime)
        .options(
            selectinload(
                Showtime.movie
            ),
            selectinload(
                Showtime.screen
            )
        )
        .where(
            Showtime.id ==
            data.showtime_id
        )
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

    valid_lock = await verify_locks(
        data.showtime_id,
        seat_ids,
        data.lock_token
    )

    if not valid_lock:

        raise HTTPException(
            409,
            "Seat lock expired. Please select the seats again."
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
            "Invalid seats"
        )

    food_ids = [
        item.food_item_id
        for item in data.food
    ]

    food_map = {}

    if food_ids:

        foods = (
            await db.scalars(
                select(FoodItem)
                .where(
                    FoodItem.id.in_(
                        food_ids
                    ),
                    FoodItem.available == True
                )
            )
        ).all()

        food_map = {
            food.id: food
            for food in foods
        }

        if len(food_map) != len(
            set(food_ids)
        ):

            raise HTTPException(
                400,
                "Invalid food item"
            )

    seat_total = sum(
        (
            seat.price
            for seat in seats
        ),
        Decimal("0")
    )

    food_total = sum(
        (
            food_map[
                item.food_item_id
            ].price * item.quantity
            for item in data.food
        ),
        Decimal("0")
    )

    total = (
        seat_total
        + food_total
    )

    booking = Booking(
        booking_code=
            generate_booking_code(),

        showtime_id=
            data.showtime_id,

        customer_name=
            data.customer_name,

        customer_email=
            data.customer_email,

        total_amount=
            total,

        payment_method=
            data.payment_method,

        payment_status=
            "success",

        status=
            "confirmed"
    )

    db.add(booking)

    await db.flush()

    for seat in seats:

        db.add(
            BookingSeat(
                booking_id=booking.id,
                seat_id=seat.id,
                price=seat.price
            )
        )

    for item in data.food:

        db.add(
            BookingFood(
                booking_id=booking.id,
                food_item_id=
                    item.food_item_id,
                quantity=
                    item.quantity,
                price=
                    food_map[
                        item.food_item_id
                    ].price
            )
        )

    await db.commit()

    await release_locks(
        data.showtime_id,
        seat_ids,
        data.lock_token
    )

    return BookingResponse(
        booking_code=
            booking.booking_code,

        movie_title=
            showtime.movie.title,

        show_date=
            showtime.show_date,

        show_time=
            showtime.show_time,

        screen_number=
            showtime.screen.screen_number,

        seats=[
            seat.seat_number
            for seat in seats
        ],

        food=[
            {
                "name":
                    food_map[
                        item.food_item_id
                    ].name,

                "quantity":
                    item.quantity,

                "price":
                    food_map[
                        item.food_item_id
                    ].price
            }

            for item in data.food
        ],

        total_amount=
            total,

        payment_method=
            data.payment_method,

        status=
            booking.status,

        customer_name=
            booking.customer_name,

        booked_at=
            booking.booked_at.isoformat()
    )