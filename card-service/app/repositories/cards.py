from typing import Any

from app.core.config import settings
from app.schemas.cards import CardResponse
from app.services.cards import generate_card


class CardRepository:
    def __init__(self, redis_client: Any):
        self.redis_client = redis_client

    def key(self, game_id: str, user_id: str) -> str:
        return f"{settings.redis_key_prefix}:cards:{game_id}:{user_id}"

    async def get(self, game_id: str, user_id: str) -> CardResponse | None:
        raw_card = await self.redis_client.get(self.key(game_id, user_id))
        if raw_card is None:
            return None

        return CardResponse.model_validate_json(raw_card)

    async def save(self, card: CardResponse) -> CardResponse:
        await self.redis_client.set(
            self.key(card.game_id, card.user_id),
            card.model_dump_json(),
        )
        return card

    async def create(self, game_id: str, user_id: str) -> CardResponse:
        existing_card = await self.get(game_id, user_id)
        if existing_card is not None:
            return existing_card

        card = generate_card(game_id=game_id, user_id=user_id)
        return await self.save(card)
