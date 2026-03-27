import logging
import time
import uuid

from fastapi import FastAPI, Request
from fastapi.openapi.utils import get_openapi

from app.api.routes import router
from app.core.config import settings
from app.core.logging import setup_logging

setup_logging(settings.log_level)

logger = logging.getLogger("app.request")

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        routes=app.routes,
        description=app.description,
    )

    # 强制把 images 修正为 Swagger 能正确识别的多文件上传格式
    body_schema = (
        openapi_schema
        .get("components", {})
        .get("schemas", {})
        .get("Body_analyze_image_v1_image_analyze_post")
    )

    if body_schema and "properties" in body_schema and "images" in body_schema["properties"]:
        body_schema["properties"]["images"] = {
            "type": "array",
            "title": "Images",
            "description": "上传单张或多张饮食图片",
            "items": {
                "type": "string",
                "format": "binary",
            },
        }

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


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