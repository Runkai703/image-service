import logging
import time
import uuid

from fastapi import FastAPI, Request

from app.api.routes import router
from app.core.config import settings
from app.core.logging import setup_logging

setup_logging(settings.log_level)

logger = logging.getLogger("app.request")

app = FastAPI(title=settings.app_name, version="0.1.0")


@app.middleware("http")
async def add_request_id_middleware(request: Request, call_next):
    request_id = f"img_{uuid.uuid4().hex[:12]}"
    request.state.request_id = request_id
    start_time = time.perf_counter()

    logger.info(
        "request started",
        extra={
            "request_id": request_id,
            "event": "request_started",
            "method": request.method,
            "path": request.url.path,
        },
    )

    try:
        response = await call_next(request)
    except Exception:
        duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
        logger.exception(
            "request failed",
            extra={
                "request_id": request_id,
                "event": "request_failed",
                "method": request.method,
                "path": request.url.path,
                "duration_ms": duration_ms,
            },
        )
        raise

    response.headers["X-Request-Id"] = request_id
    duration_ms = round((time.perf_counter() - start_time) * 1000, 2)

    if response.status_code >= 500:
        logger.error(
            "request returned server error",
            extra={
                "request_id": request_id,
                "event": "request_server_error",
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_ms": duration_ms,
            },
        )
    elif response.status_code >= 400:
        logger.warning(
            "request returned client error",
            extra={
                "request_id": request_id,
                "event": "request_client_error",
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_ms": duration_ms,
            },
        )

    logger.info(
        "request completed",
        extra={
            "request_id": request_id,
            "event": "request_completed",
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "duration_ms": duration_ms,
        },
    )
    return response


app.include_router(router)


@app.get("/")
def root() -> dict:
    return {
        "message": f"{settings.app_name} is running",
        "env": settings.app_env,
    }