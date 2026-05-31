import httpx

from app.core.config import settings
from app.schemas.winners import WinnerClaimMessage
from app.services.evaluator import has_bingo
from app.services.integrations import (
    fetch_game_state,
    fetch_lobby_room,
    fetch_winner_check_data,
    finish_lobby_room,
    reward_winner,
)
from app.services.storage import WinnerStorage


async def process_winner_claim(
    payload: WinnerClaimMessage,
    storage: WinnerStorage,
) -> None:
    await storage.update_claim(payload.claim_id, "processing")

    try:
        card = await fetch_winner_check_data(
            game_id=payload.game_id,
            token=payload.token,
        )
        game_state = await fetch_game_state(payload.game_id)
        lobby_room = await fetch_lobby_room(payload.game_id)
    except httpx.HTTPError as exc:
        await storage.update_claim(
            payload.claim_id,
            "verification_failed",
            reason=f"Dependency request failed: {exc}",
        )
        return

    if not has_bingo(card, game_state.drawn_balls, lobby_room.winning_pattern):
        await storage.update_claim(
            payload.claim_id,
            "rejected",
            reason="Selected BINGO pattern is not completed",
        )
        return

    reward_status = "paid"
    try:
        await reward_winner(
            user_id=payload.user_id,
            token=payload.token,
            amount=settings.reward_amount,
        )
    except httpx.HTTPError:
        reward_status = "failed"

    await storage.save_winner(
        game_id=payload.game_id,
        user_id=payload.user_id,
        claim_id=payload.claim_id,
        reward_amount=settings.reward_amount,
        reward_status=reward_status,
    )
    try:
        await finish_lobby_room(payload.game_id)
    except httpx.HTTPError:
        pass

    await storage.update_claim(
        payload.claim_id,
        "won" if reward_status == "paid" else "reward_failed",
        reason=None if reward_status == "paid" else "Reward request failed",
    )
