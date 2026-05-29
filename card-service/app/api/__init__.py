from fastapi import APIRouter

from app.api.routes.cards import router as cards_router


router = APIRouter()
router.include_router(cards_router)
