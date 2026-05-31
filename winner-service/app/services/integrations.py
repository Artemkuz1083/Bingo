from decimal import Decimal

import httpx

from app.core.config import settings
from app.schemas.winners import GameState, LobbyRoom, WinnerCheckData


def auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


async def fetch_winner_check_data(
    game_id: str,
    token: str,
) -> WinnerCheckData:
    async with httpx.AsyncClient(timeout=settings.http_timeout_seconds) as client:
        response = await client.get(
            f"{settings.card_service_url}/games/{game_id}/cards/me/winner-data",
            headers=auth_headers(token),
        )
        response.raise_for_status()
        return WinnerCheckData.model_validate(response.json())


async def fetch_game_state(game_id: str) -> GameState:
    async with httpx.AsyncClient(timeout=settings.http_timeout_seconds) as client:
        response = await client.get(
            f"{settings.game_engine_service_url}/game/{game_id}/state",
        )
        response.raise_for_status()
        return GameState.model_validate(response.json())


async def fetch_lobby_room(game_id: str) -> LobbyRoom:
    async with httpx.AsyncClient(timeout=settings.http_timeout_seconds) as client:
        response = await client.get(f"{settings.lobby_service_url}/rooms/{game_id}")
        response.raise_for_status()
        return LobbyRoom.model_validate(response.json())


async def reward_winner(
    user_id: str,
    token: str,
    amount: Decimal,
) -> None:
    async with httpx.AsyncClient(timeout=settings.http_timeout_seconds) as client:
        response = await client.patch(
            f"{settings.user_service_url}/users/{user_id}/balance",
            headers=auth_headers(token),
            json={"amount": str(amount)},
        )
        response.raise_for_status()


async def finish_lobby_room(game_id: str) -> None:
    if not settings.lobby_service_url or not settings.internal_service_token:
        return

    async with httpx.AsyncClient(timeout=settings.http_timeout_seconds) as client:
        response = await client.post(
            f"{settings.lobby_service_url}/internal/rooms/{game_id}/finish",
            headers={"X-Internal-Service-Token": settings.internal_service_token},
        )
        response.raise_for_status()
