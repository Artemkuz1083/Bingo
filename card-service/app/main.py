from fastapi import FastAPI

from app.api import router
from app.core.config import settings


app = FastAPI(title="Card Service")
app.include_router(router)


@app.get("/health")
def health_check():
    return {
        "service": settings.service_name,
        "status": "ok",
    }
