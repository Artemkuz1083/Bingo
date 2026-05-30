from fastapi import FastAPI
from app.api import game
from app.core.config import settings

app = FastAPI(title="BINGO Game Engine Service")


app.include_router(game.router, tags=["engine"])


@app.get("/health")
async def health():
    return {
        "service": settings.service_name,
        "status": "ok",
    }