from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import game
from app.core.config import settings

app = FastAPI(title="BINGO Game Engine Service")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(game.router, prefix="/game", tags=["engine"])


@app.get("/health")
async def health():
    return {
        "service": settings.service_name,
        "status": "ok",
    }
