from contextlib import asynccontextmanager

from fastapi import FastAPI

from fastapi.middleware.cors import (
    CORSMiddleware
)

from sqlalchemy import text

from app.database import (
    engine,
    Base
)

from app.redis_client import redis

import app.models

from app.routers import (
    auth,
    movies,
    food,
    showtimes,
    bookings,
    admin
)


@asynccontextmanager
async def lifespan(app: FastAPI):

    async with engine.begin() as connection:

        await connection.run_sync(
            Base.metadata.create_all
        )

    await redis.ping()

    yield

    await redis.close()

    await engine.dispose()


app = FastAPI(
    title="CineSphere API",
    version="1.0.0",
    lifespan=lifespan
)


app.add_middleware(
    CORSMiddleware,

    allow_origins=["*"],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"]
)


app.include_router(
    auth.router,
    prefix="/api"
)

app.include_router(
    movies.router,
    prefix="/api"
)

app.include_router(
    food.router,
    prefix="/api"
)

app.include_router(
    showtimes.router,
    prefix="/api"
)

app.include_router(
    bookings.router,
    prefix="/api"
)

app.include_router(
    admin.router,
    prefix="/api"
)


@app.get("/")
async def root():

    return {
        "message":
            "CineSphere backend is running"
    }


@app.get("/health")
async def health():

    async with engine.connect() as connection:

        result = await connection.execute(
            text("SELECT 1")
        )

    await redis.ping()

    return {
        "status": "ok",
        "database": "connected",
        "redis": "connected",
        "test": result.scalar()
    }