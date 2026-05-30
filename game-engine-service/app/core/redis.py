import redis.asyncio as redis

from app.core.config import settings


redis_client = redis.Redis(
    host=settings.redis_host,
    port=settings.redis_port,
    db=settings.redis_db,
    decode_responses=True,
)

def _prefix(room_id: str) -> str:
    return f"{settings.redis_key_prefix}:room:{room_id}"

# Set всех выпавших шаров
def key_drawn(room_id: str) -> str:
    return f"{_prefix(room_id)}:drawn"

# Последний выпавший шар
def key_last(room_id: str) -> str:
    return f"{_prefix(room_id)}:last"

# 1-игра идет, 0-игра остановлена
def key_active(room_id: str) -> str:
    return f"{_prefix(room_id)}:active"

# время старта игры
def key_started_at(room_id: str) -> str:
    return f"{_prefix(room_id)}:started_at"

# List всех игроков комнаты
def key_players(room_id: str) -> str:
    return f"{_prefix(room_id)}:players"