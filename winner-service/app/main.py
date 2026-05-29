from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.winners import router
from app.core.config import settings
from app.services.queue import ensure_winner_claims_queue


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    await ensure_winner_claims_queue()
    yield


app = FastAPI(title=settings.service_name, lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok", "service": settings.service_name}
