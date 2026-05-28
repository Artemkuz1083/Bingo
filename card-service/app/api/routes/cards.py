from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_card_repository
from app.core.security import get_current_user_id
from app.repositories.cards import CardRepository
from app.schemas.cards import CardPreviewRequest, CardResponse
from app.services.cards import generate_card


router = APIRouter(tags=["cards"])


@router.post("/cards/preview", response_model=CardResponse)
def preview_card(payload: CardPreviewRequest) -> CardResponse:
    return generate_card(game_id=payload.game_id, user_id=payload.user_id)


@router.post(
    "/games/{game_id}/cards/me",
    response_model=CardResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_my_card(
    game_id: str,
    user_id: str = Depends(get_current_user_id),
    repository: CardRepository = Depends(get_card_repository),
) -> CardResponse:
    return await repository.create(game_id=game_id, user_id=user_id)


@router.get("/games/{game_id}/cards/me", response_model=CardResponse)
async def get_my_card(
    game_id: str,
    user_id: str = Depends(get_current_user_id),
    repository: CardRepository = Depends(get_card_repository),
) -> CardResponse:
    card = await repository.get(game_id=game_id, user_id=user_id)
    if card is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Card not found",
        )

    return card
