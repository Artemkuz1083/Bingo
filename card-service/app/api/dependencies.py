from app.core.redis import redis_client
from app.repositories.cards import CardRepository


def get_card_repository() -> CardRepository:
    return CardRepository(redis_client)
