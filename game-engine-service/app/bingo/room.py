from app.bingo.enums import GameStatus
from app.core.redis import redis_client

class BingoRoom:
    def __init__(self, room_id: str):
        self.room_id = room_id

    @property
    def drawn_key(self):
        return f"bingo:{self.room_id}:drawn"

    @property
    def last_ball_key(self):
        return f"bingo:{self.room_id}:last_ball"

    @property
    def status_key(self):
        return f"bingo:{self.room_id}:status"

    async def save_ball(self, ball: str):
        await redis_client.sadd(self.drawn_key, ball)
        await redis_client.set(self.last_ball_key, ball)

    async def set_status(self, status: GameStatus):
        await redis_client.set(
            self.status_key,
            status.value
        )

    async def get_status(self) -> GameStatus | None:
        value = await redis_client.get(self.status_key)

        if value is None:
            return None

        return GameStatus(value)