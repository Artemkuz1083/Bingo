from fastapi import APIRouter

from app.schemas.cards import CardPreviewRequest, CardResponse
from app.services.cards import generate_card


router = APIRouter(prefix="/cards", tags=["cards"])


@router.post("/preview", response_model=CardResponse)
def preview_card(payload: CardPreviewRequest) -> CardResponse:
    return generate_card(game_id=payload.game_id, user_id=payload.user_id)
