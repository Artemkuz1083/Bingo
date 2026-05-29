from fastapi import APIRouter, Depends, HTTPException, status

from app.core.security import AuthContext, get_auth_context
from app.schemas.winners import ClaimResponse, WinnerResponse
from app.services.queue import publish_winner_claim
from app.services.storage import WinnerStorage, get_winner_storage


router = APIRouter(tags=["winners"])


@router.post(
    "/games/{game_id}/winner-claims",
    response_model=ClaimResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def submit_winner_claim(
    game_id: str,
    auth: AuthContext = Depends(get_auth_context),
    storage: WinnerStorage = Depends(get_winner_storage),
) -> ClaimResponse:
    claim = await storage.create_claim(game_id=game_id, user_id=auth.user_id)
    await publish_winner_claim(
        claim_id=claim.claim_id,
        game_id=game_id,
        user_id=auth.user_id,
        token=auth.token,
    )
    return claim


@router.get("/games/{game_id}/winner", response_model=WinnerResponse)
async def get_game_winner(
    game_id: str,
    storage: WinnerStorage = Depends(get_winner_storage),
) -> WinnerResponse:
    winner = await storage.get_winner(game_id)
    if winner is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Winner not found",
        )
    return winner


@router.get(
    "/games/{game_id}/winner-claims/{claim_id}",
    response_model=ClaimResponse,
)
async def get_winner_claim(
    game_id: str,
    claim_id: str,
    storage: WinnerStorage = Depends(get_winner_storage),
) -> ClaimResponse:
    claim = await storage.get_claim(claim_id)
    if claim is None or claim.game_id != game_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Winner claim not found",
        )
    return claim
