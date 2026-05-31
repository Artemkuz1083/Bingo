import httpx

from app.config import settings
from app.models import Room


def notify_game_started(room: Room) -> None:
    if not settings.game_engine_service_url:
        return

    player_user_ids = [player.user_id for player in room.players]
    with httpx.Client(timeout=settings.http_timeout_seconds) as client:
        response = client.post(
            f"{settings.game_engine_service_url}/game/{room.id}/start",
            json={
                "room_id": room.id,
                "player_user_ids": player_user_ids,
            },
        )
        response.raise_for_status()


def notify_game_finished(room: Room) -> None:
    if not settings.game_engine_service_url:
        return

    with httpx.Client(timeout=settings.http_timeout_seconds) as client:
        response = client.post(
            f"{settings.game_engine_service_url}/game/{room.id}/stop",
        )
        if response.status_code == 404:
            return
        response.raise_for_status()


def draw_game_ball(room: Room) -> dict:
    if not settings.game_engine_service_url:
        raise RuntimeError("Game engine service URL is not configured")

    with httpx.Client(timeout=settings.http_timeout_seconds) as client:
        response = client.post(f"{settings.game_engine_service_url}/game/{room.id}/draw")
        response.raise_for_status()
        return response.json()
