from fastapi import APIRouter
from app.core.redis import redis_client

router = APIRouter()

"""Получение состояние комнаты"""
@router.get("/game/{room_id}/state")
async def get_game_state(room_id: str):
    drawn = await redis_client.smembers(
        f"bingo:{room_id}:drawn"
    )

    last_ball = await redis_client.get(
        f"bingo:{room_id}:last_ball"
    )

    status = await redis_client.get(
        f"bingo:{room_id}:status"
    )

    return {
        "room_id": room_id,
        "status": status,
        "last_ball": last_ball,
        "drawn_balls": list(drawn),
    }