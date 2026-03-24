import logging

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile

from app.core.config import settings
from app.core.security import verify_api_key
from app.schemas.image_analysis import ImageAnalysisResult
from app.services.image_chain import analyze_image_with_llm

router = APIRouter()
logger = logging.getLogger("app.image")


@router.post(
    "/v1/image/analyze",
    response_model=ImageAnalysisResult,
    dependencies=[Depends(verify_api_key)],
)
async def analyze_image(
    request: Request,
    image: UploadFile = File(...),
    user_name: str = Form("用户"),
    scene_hint: str = Form("auto"),
) -> ImageAnalysisResult:
    request_id = request.state.request_id

    logger.info(
        "image analyze request received",
        extra={
            "request_id": request_id,
            "event": "image_analyze_request_received",
            "path": request.url.path,
            "upload_filename": image.filename,
            "content_type": image.content_type,
            "user_name": user_name,
            "scene_hint": scene_hint,
        },
    )

    if not image.filename:
        logger.warning(
            "missing filename",
            extra={
                "request_id": request_id,
                "event": "image_validation_failed",
                "path": request.url.path,
                "reason": "missing_filename",
            },
        )
        raise HTTPException(status_code=400, detail="未检测到上传文件")

    if image.content_type not in ["image/jpeg", "image/png", "image/webp"]:
        logger.warning(
            "unsupported image content type",
            extra={
                "request_id": request_id,
                "event": "image_validation_failed",
                "path": request.url.path,
                "content_type": image.content_type,
                "reason": "unsupported_content_type",
            },
        )
        raise HTTPException(status_code=400, detail="不支持的图片类型")

    image_bytes = await image.read()

    if not image_bytes:
        logger.warning(
            "empty image content",
            extra={
                "request_id": request_id,
                "event": "image_validation_failed",
                "path": request.url.path,
                "upload_filename": image.filename,
                "reason": "empty_file",
            },
        )
        raise HTTPException(status_code=400, detail="图片内容为空")

    max_upload_bytes = settings.max_upload_mb * 1024 * 1024
    if len(image_bytes) > max_upload_bytes:
        logger.warning(
            "image size exceeds limit",
            extra={
                "request_id": request_id,
                "event": "image_validation_failed",
                "path": request.url.path,
                "upload_filename": image.filename,
                "size_bytes": len(image_bytes),
                "max_upload_mb": settings.max_upload_mb,
                "reason": "file_too_large",
            },
        )
        raise HTTPException(
            status_code=400,
            detail=f"图片大小超过限制，当前最大允许 {settings.max_upload_mb}MB",
        )

    logger.info(
        "start image analysis",
        extra={
            "request_id": request_id,
            "event": "image_analysis_started",
            "path": request.url.path,
            "upload_filename": image.filename,
            "content_type": image.content_type,
            "size_bytes": len(image_bytes),
            "user_name": user_name,
            "scene_hint": scene_hint,
        },
    )

    result = analyze_image_with_llm(
        image_bytes=image_bytes,
        content_type=image.content_type,
        request_id=request_id,
        user_name=user_name,
        scene_hint=scene_hint,
    )

    if result.scene_type == "uncertain":
        logger.warning(
            "image analysis returned fallback result",
            extra={
                "request_id": request_id,
                "event": "image_analysis_fallback",
                "path": request.url.path,
                "warnings": result.warnings,
            },
        )

    logger.info(
        "image analysis completed",
        extra={
            "request_id": request_id,
            "event": "image_analysis_completed",
            "path": request.url.path,
            "scene_type": result.scene_type,
            "confidence": result.confidence,
            "has_calories": result.calories is not None,
        },
    )

    return result