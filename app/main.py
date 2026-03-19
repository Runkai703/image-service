import logging
import uuid

from fastapi import FastAPI, Request

from app.api.routes import router
from app.core.config import settings

logger = logging.getLogger("uvicorn.error")

app = FastAPI(title=settings.app_name, version="0.1.0")


@app.middleware("http")
async def add_request_id_middleware(request: Request, call_next):
    request_id = f"img_{uuid.uuid4().hex[:12]}"
    request.state.request_id = request_id

    logger.info("request started | request_id=%s | path=%s", request_id, request.url.path)

    try:
        response = await call_next(request)
    except Exception:
        logger.exception(
            "request failed | request_id=%s | path=%s",
            request_id,
            request.url.path,
        )
        raise

    response.headers["X-Request-Id"] = request_id

    if response.status_code >= 500:
        logger.error(
            "request returned server error | request_id=%s | path=%s | status_code=%s",
            request_id,
            request.url.path,
            response.status_code,
        )
    elif response.status_code >= 400:
        logger.warning(
            "request returned client error | request_id=%s | path=%s | status_code=%s",
            request_id,
            request.url.path,
            response.status_code,
        )

    logger.info(
        "request completed | request_id=%s | path=%s | status_code=%s",
        request_id,
        request.url.path,
        response.status_code,
    )
    return response


app.include_router(router)


@app.get("/")
def root() -> dict:
    return {
        "message": f"{settings.app_name} is running",
        "env": settings.app_env,
    }