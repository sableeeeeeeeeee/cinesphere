from datetime import date, time
from decimal import Decimal

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field
)


class UserCreate(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=100
    )

    email: EmailStr

    password: str = Field(
        min_length=6,
        max_length=100
    )


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class MovieCreate(BaseModel):
    id: str | None = None
    title: str
    genre: str = "Drama"
    language: str = "English"
    duration: str = "2h 00m"
    cert: str = "UA16+"
    score: float | None = None
    tagline: str | None = None
    synopsis: str | None = None
    poster: str | None = None
    status: str = "showing"
    release_label: str | None = None
    leave_label: str | None = None


class MovieResponse(MovieCreate):
    id: str

    model_config = ConfigDict(
        from_attributes=True
    )


class ShowtimeCreate(BaseModel):
    movie_id: str
    screen_id: int
    show_date: date
    show_time: time


class ShowtimeResponse(BaseModel):
    id: int
    movie_id: str
    screen_id: int
    show_date: date
    show_time: time
    screen_number: int

    model_config = ConfigDict(
        from_attributes=True
    )


class SeatResponse(BaseModel):
    id: int
    seat_number: str
    row_name: str
    tier: str
    price: Decimal
    status: str


class FoodResponse(BaseModel):
    id: int
    name: str
    description: str | None
    price: Decimal
    emoji: str | None
    available: bool

    model_config = ConfigDict(
        from_attributes=True
    )


class LockSeatsRequest(BaseModel):
    seat_ids: list[int] = Field(
        min_length=1
    )


class LockSeatsResponse(BaseModel):
    token: str
    expires_in: int
    seat_ids: list[int]


class BookingFoodItem(BaseModel):
    food_item_id: int
    quantity: int = Field(gt=0)


class BookingCreate(BaseModel):
    showtime_id: int

    seat_ids: list[int] = Field(
        min_length=1
    )

    lock_token: str

    customer_name: str

    customer_email: EmailStr | None = None

    payment_method: str = "card"

    food: list[BookingFoodItem] = []


class BookingResponse(BaseModel):
    booking_code: str
    movie_title: str
    show_date: date
    show_time: time
    screen_number: int
    seats: list[str]
    food: list[dict]
    total_amount: Decimal
    payment_method: str
    status: str
    customer_name: str
    booked_at: str