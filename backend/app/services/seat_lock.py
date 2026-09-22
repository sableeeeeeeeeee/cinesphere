import secrets

from app.redis_client import redis


LOCK_SECONDS = 300


def lock_key(
    showtime_id: int,
    seat_id: int
) -> str:

    return (
        f"cinesphere:"
        f"lock:"
        f"{showtime_id}:"
        f"{seat_id}"
    )


async def lock_seats(
    showtime_id: int,
    seat_ids: list[int]
):

    token = secrets.token_urlsafe(24)

    keys = [
        lock_key(showtime_id, seat_id)
        for seat_id in seat_ids
    ]

    script = """
    for i,key in ipairs(KEYS) do
        if redis.call('EXISTS', key) == 1 then
            return 0
        end
    end

    for i,key in ipairs(KEYS) do
        redis.call(
            'SET',
            key,
            ARGV[1],
            'EX',
            ARGV[2]
        )
    end

    return 1
    """

    result = await redis.eval(
        script,
        len(keys),
        *keys,
        token,
        LOCK_SECONDS
    )

    if result != 1:
        return None

    return token


async def verify_locks(
    showtime_id: int,
    seat_ids: list[int],
    token: str
):

    for seat_id in seat_ids:

        value = await redis.get(
            lock_key(
                showtime_id,
                seat_id
            )
        )

        if value != token:
            return False

    return True


async def release_locks(
    showtime_id: int,
    seat_ids: list[int],
    token: str
):

    script = """
    for i,key in ipairs(KEYS) do

        if redis.call(
            'GET',
            key
        ) == ARGV[1] then

            redis.call(
                'DEL',
                key
            )

        end

    end

    return 1
    """

    keys = [
        lock_key(showtime_id, seat_id)
        for seat_id in seat_ids
    ]

    if keys:

        await redis.eval(
            script,
            len(keys),
            *keys,
            token
        )