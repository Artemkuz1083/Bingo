from datetime import UTC, datetime
from decimal import Decimal
from typing import Any
from uuid import uuid4

from app.core.config import settings
from app.core.redis import redis_client
from app.schemas.winners import ClaimResponse, ClaimStatus, WinnerResponse


def now_utc() -> datetime:
    return datetime.now(UTC)


class WinnerStorage:
    def __init__(self, redis: Any):
        self.redis = redis

    def claim_key(self, claim_id: str) -> str:
        return f"{settings.redis_key_prefix}:winner:claims:{claim_id}"

    def game_winner_key(self, game_id: str) -> str:
        return f"{settings.redis_key_prefix}:winner:games:{game_id}"

    async def create_claim(self, game_id: str, user_id: str) -> ClaimResponse:
        timestamp = now_utc()
        claim = ClaimResponse(
            claim_id=str(uuid4()),
            game_id=game_id,
            user_id=user_id,
            status="queued",
            created_at=timestamp,
            updated_at=timestamp,
        )
        await self.save_claim(claim)
        return claim

    async def get_claim(self, claim_id: str) -> ClaimResponse | None:
        raw_claim = await self.redis.get(self.claim_key(claim_id))
        if raw_claim is None:
            return None
        return ClaimResponse.model_validate_json(raw_claim)

    async def save_claim(self, claim: ClaimResponse) -> ClaimResponse:
        await self.redis.set(self.claim_key(claim.claim_id), claim.model_dump_json())
        return claim

    async def update_claim(
        self,
        claim_id: str,
        status: ClaimStatus,
        reason: str | None = None,
    ) -> ClaimResponse | None:
        claim = await self.get_claim(claim_id)
        if claim is None:
            return None

        updated = claim.model_copy(
            update={
                "status": status,
                "reason": reason,
                "updated_at": now_utc(),
            },
        )
        await self.save_claim(updated)
        return updated

    async def get_winner(self, game_id: str) -> WinnerResponse | None:
        raw_winner = await self.redis.get(self.game_winner_key(game_id))
        if raw_winner is None:
            return None
        return WinnerResponse.model_validate_json(raw_winner)

    async def save_winner(
        self,
        game_id: str,
        user_id: str,
        claim_id: str,
        reward_amount: Decimal,
        reward_status: str,
    ) -> WinnerResponse:
        existing = await self.get_winner(game_id)
        if existing is not None:
            return existing

        winner = WinnerResponse(
            game_id=game_id,
            user_id=user_id,
            claim_id=claim_id,
            reward_amount=reward_amount,
            reward_status=reward_status,
            created_at=now_utc(),
        )
        await self.redis.set(
            self.game_winner_key(game_id),
            winner.model_dump_json(),
            nx=True,
        )
        return await self.get_winner(game_id) or winner


def get_winner_storage() -> WinnerStorage:
    return WinnerStorage(redis_client)
