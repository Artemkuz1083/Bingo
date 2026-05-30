import asyncio
import logging
import time

import redis.asyncio as aioredis
from app.core.config import settings

from app.engine.balls import build_shuffle_pool, parse_ball, letter
from app.core.redis import (
    redis_client,
    key_active,
    key_drawn,
    key_last,
    key_started_at, key_players,
)

logger = logging.getLogger(__name__)


_tasks: dict[str, asyncio.Task] = {}

# True - игра успешно создана
# False - игра уже создана
async def start_game(room_id: str, player_user_ids: list[str]) -> bool:
    if room_id in _tasks and not _tasks[room_id].done():
        return False

    await redis_client.delete(key_drawn(room_id), key_last(room_id), key_players(room_id))
    await redis_client.set(key_active(room_id), "1")
    await redis_client.set(key_started_at(room_id), str(int(time.time())))

    if player_user_ids:
        await redis_client.rpush(key_players(room_id), *player_user_ids)

    task = asyncio.create_task(
        _draw_loop(room_id),
        name=f"draw-loop-{room_id}",
    )
    _tasks[room_id] = task
    logger.info(f"Комната {room_id}: игра началась!")
    return True

# True - игра успешно остановлена
# False - игра уже остановлена
async def stop_game(room_id: str) -> bool:
    is_active = await redis_client.get(key_active(room_id))
    if is_active != "1":
        return False
    await redis_client.set(key_active(room_id), "0")
    logger.info(f"Комната {room_id}: получена команда остановки")
    return True

async def get_state(room_id: str) -> dict:
    drawn_with_scores = await redis_client.zrange(key_drawn(room_id), 0, -1, withscores=True)
    drawn_balls = [
        {
            "label": label,
            "letter": parse_ball(label)[0],
            "number": parse_ball(label)[1],
            "order": int(score),
        }
        for label, score in drawn_with_scores
    ]

    last = await redis_client.get(key_last(room_id))
    active = await redis_client.get(key_active(room_id))
    started_at = await redis_client.get(key_started_at(room_id))
    players = await redis_client.lrange(key_players(room_id), 0, -1)

    last_ball = None
    if last:
        letter, number = parse_ball(last)
        last_ball = {"label": last, "letter": letter, "number": number}

    return {
        "room_id": room_id,
        "is_active": active == "1",
        "started_at": int(started_at) if started_at else None,
        "drawn_count": len(drawn_balls),
        "remaining_count": 75 - len(drawn_balls),
        "last_ball": last_ball,
        "drawn_balls": drawn_balls,
        "player_user_ids": players,
    }

async def _draw_loop(room_id: str, redis: aioredis.Redis):
    pool = build_shuffle_pool()
    interval = settings.draw_interval_seconds

    for order, label in enumerate(pool, start=1):
        active = await redis.get(key_active(room_id))
        if active != "1":
            logger.info(f"Комната {room_id}: была остановлена после команды stop.")
            break

        async with redis.pipeline(transaction=True) as pipe:
            pipe.zadd(key_drawn(room_id), {label: order})
            pipe.set(key_last(room_id), label)
            await pipe.execute()

        letter, number = parse_ball(label)
        logger.info(f"Комната {room_id}: выпал шар {label} ({order})")

        await redis.publish(
            f"{settings.redis_key_prefix}:room:{room_id}:ball_drawn",
            f'{{'
            f'"room_id":"{room_id}",'
            f'"label":"{label}",'
            f'"letter":"{letter}",'
            f'"number":{number},'
            f'"order":{order}}}',
        )

        if order == 75:
            await redis.set(key_active(room_id), "0")
            logger.info(f"Комната {room_id}: все 75 шаров выпали, игра закончена")
            break

        await asyncio.sleep(interval)