from datetime import datetime, date, time
from decimal import Decimal

from sqlalchemy import (
    String,
    Integer,
    Boolean,
    DateTime,
    Date,
    Time,
    ForeignKey,
    Numeric,
    Text,
    UniqueConstraint
)

from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    name: Mapped[str] = mapped_column(String(100))

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True
    )

    password_hash: Mapped[str] = mapped_column(String(255))

    is_admin: Mapped[bool] = mapped_column(
        Boolean,
        default=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    bookings: Mapped[list["Booking"]] = relationship(
        back_populates="user"
    )


class Movie(Base):
    __tablename__ = "movies"

    id: Mapped[str] = mapped_column(
        String(100),
        primary_key=True
    )

    title: Mapped[str] = mapped_column(
        String(200)
    )

    genre: Mapped[str] = mapped_column(
        String(200),
        default="Drama"
    )

    language: Mapped[str] = mapped_column(
        String(50),
        default="English"
    )

    duration: Mapped[str] = mapped_column(
        String(30),
        default="2h 00m"
    )

    cert: Mapped[str] = mapped_column(
        String(30),
        default="UA16+"
    )

    score: Mapped[Decimal | None] = mapped_column(
        Numeric(3, 1),
        nullable=True
    )

    tagline: Mapped[str | None] = mapped_column(
        String(300),
        nullable=True
    )

    synopsis: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    poster: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    status: Mapped[str] = mapped_column(
        String(20),
        default="showing"
    )

    release_label: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    leave_label: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    showtimes: Mapped[list["Showtime"]] = relationship(
        back_populates="movie",
        cascade="all, delete-orphan"
    )


class Screen(Base):
    __tablename__ = "screens"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    screen_number: Mapped[int] = mapped_column(
        Integer,
        unique=True
    )

    name: Mapped[str] = mapped_column(
        String(100),
        default="Screen"
    )

    seats: Mapped[list["Seat"]] = relationship(
        back_populates="screen",
        cascade="all, delete-orphan"
    )

    showtimes: Mapped[list["Showtime"]] = relationship(
        back_populates="screen"
    )


class Seat(Base):
    __tablename__ = "seats"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    screen_id: Mapped[int] = mapped_column(
        ForeignKey("screens.id", ondelete="CASCADE")
    )

    seat_number: Mapped[str] = mapped_column(
        String(10)
    )

    row_name: Mapped[str] = mapped_column(
        String(2)
    )

    tier: Mapped[str] = mapped_column(
        String(20)
    )

    price: Mapped[Decimal] = mapped_column(
        Numeric(10, 2)
    )

    screen: Mapped["Screen"] = relationship(
        back_populates="seats"
    )

    __table_args__ = (
        UniqueConstraint(
            "screen_id",
            "seat_number",
            name="uq_screen_seat"
        ),
    )


class Showtime(Base):
    __tablename__ = "showtimes"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    movie_id: Mapped[str] = mapped_column(
        ForeignKey(
            "movies.id",
            ondelete="CASCADE"
        )
    )

    screen_id: Mapped[int] = mapped_column(
        ForeignKey("screens.id")
    )

    show_date: Mapped[date] = mapped_column(
        Date
    )

    show_time: Mapped[time] = mapped_column(
        Time
    )

    movie: Mapped["Movie"] = relationship(
        back_populates="showtimes"
    )

    screen: Mapped["Screen"] = relationship(
        back_populates="showtimes"
    )

    bookings: Mapped[list["Booking"]] = relationship(
        back_populates="showtime"
    )


class FoodItem(Base):
    __tablename__ = "food_items"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    name: Mapped[str] = mapped_column(
        String(100)
    )

    description: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )

    price: Mapped[Decimal] = mapped_column(
        Numeric(10, 2)
    )

    emoji: Mapped[str | None] = mapped_column(
        String(10),
        nullable=True
    )

    available: Mapped[bool] = mapped_column(
        Boolean,
        default=True
    )

    booking_items: Mapped[list["BookingFood"]] = relationship(
        back_populates="food_item"
    )


class Booking(Base):
    __tablename__ = "bookings"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    booking_code: Mapped[str] = mapped_column(
        String(30),
        unique=True,
        index=True
    )

    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"),
        nullable=True
    )

    showtime_id: Mapped[int] = mapped_column(
        ForeignKey("showtimes.id")
    )

    customer_name: Mapped[str] = mapped_column(
        String(100)
    )

    customer_email: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )

    total_amount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2)
    )

    payment_method: Mapped[str] = mapped_column(
        String(30)
    )

    payment_status: Mapped[str] = mapped_column(
        String(30),
        default="success"
    )

    status: Mapped[str] = mapped_column(
        String(30),
        default="confirmed"
    )

    booked_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    user: Mapped[User | None] = relationship(
        back_populates="bookings"
    )

    showtime: Mapped[Showtime] = relationship(
        back_populates="bookings"
    )

    seats: Mapped[list["BookingSeat"]] = relationship(
        back_populates="booking",
        cascade="all, delete-orphan"
    )

    food: Mapped[list["BookingFood"]] = relationship(
        back_populates="booking",
        cascade="all, delete-orphan"
    )


class BookingSeat(Base):
    __tablename__ = "booking_seats"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    booking_id: Mapped[int] = mapped_column(
        ForeignKey(
            "bookings.id",
            ondelete="CASCADE"
        )
    )

    seat_id: Mapped[int] = mapped_column(
        ForeignKey("seats.id")
    )

    price: Mapped[Decimal] = mapped_column(
        Numeric(10, 2)
    )

    booking: Mapped[Booking] = relationship(
        back_populates="seats"
    )


class BookingFood(Base):
    __tablename__ = "booking_food"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    booking_id: Mapped[int] = mapped_column(
        ForeignKey(
            "bookings.id",
            ondelete="CASCADE"
        )
    )

    food_item_id: Mapped[int] = mapped_column(
        ForeignKey("food_items.id")
    )

    quantity: Mapped[int] = mapped_column(
        Integer
    )

    price: Mapped[Decimal] = mapped_column(
        Numeric(10, 2)
    )

    booking: Mapped[Booking] = relationship(
        back_populates="food"
    )

    food_item: Mapped[FoodItem] = relationship(
        back_populates="booking_items"
    )