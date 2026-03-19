from fastapi import FastAPI

from app.api.routes import router
from app.core.config import settings

app = FastAPI(title=settings.app_name, version="0.1.0")

app.include_router(router)


@app.get("/")
def root() -> dict:
    return {
        "message": f"{settings.app_name} is running",
        "env": settings.app_env,
    }