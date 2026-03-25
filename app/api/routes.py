import asyncio
import logging

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile

from app.core.config import settings
from app.core.security import verify_api_key
from app.schemas.image_analysis import ImageAnalysisLiteResponse, ImageAnalysisResult
from app.services.image_chain import analyze_image_with_llm
from app.services.aggregation import aggregate_results

router = APIRouter()
logger = logging.getLogger("app.image")


@router.post(
    "/v1/image/analyze",
    response_model=ImageAnalysisLiteResponse,
    dependencies=[Depends(verify_api_key)],
)
async def analyze_image(
    request: Request,
    images: list[UploadFile] | None = File(None),
    image: UploadFile | None = File(None),
    user_name: str = Form("用户"),
    scene_hint: str = Form("auto"),
) -> ImageAnalysisLiteResponse:
    request_id = request.state.request_id

    # 统一兼容单图 / 多图输入
    final_images: list[UploadFile] = []

    if images:
        final_images.extend(images)

    if image:
        final_images.append(image)

    logger.info(
        "image analyze request received",
        extra={
            "request_id": request_id,
            "event": "image_analyze_request_received",
            "path": request.url.path,
            "upload_filename": [img.filename for img in final_images],
            "content_type": [img.content_type for img in final_images],
            "user_name": user_name,
            "scene_hint": scene_hint,
        },
    )

    if not final_images:
        logger.warning(
            "missing uploaded files",
            extra={
                "request_id": request_id,
                "event": "image_validation_failed",
                "path": request.url.path,
                "reason": "missing_files",
            },
        )
        raise HTTPException(status_code=400, detail="未检测到上传文件")

    validated_images: list[tuple[bytes, str, str]] = []

    for img in final_images:
        if not img.filename:
            logger.warning(
                "missing filename",
                extra={
                    "request_id": request_id,
                    "event": "image_validation_failed",
                    "path": request.url.path,
                    "reason": "missing_filename",
                },
            )
            raise HTTPException(status_code=400, detail="未检测到上传文件名")

        if img.content_type not in ["image/jpeg", "image/png", "image/webp"]:
            logger.warning(
                "unsupported image content type",
                extra={
                    "request_id": request_id,
                    "event": "image_validation_failed",
                    "path": request.url.path,
                    "content_type": img.content_type,
                    "reason": "unsupported_content_type",
                },
            )
            raise HTTPException(status_code=400, detail="不支持的图片类型")

        image_bytes = await img.read()

        if not image_bytes:
            logger.warning(
                "empty image content",
                extra={
                    "request_id": request_id,
                    "event": "image_validation_failed",
                    "path": request.url.path,
                    "upload_filename": img.filename,
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
                    "upload_filename": img.filename,
                    "size_bytes": len(image_bytes),
                    "max_upload_mb": settings.max_upload_mb,
                    "reason": "file_too_large",
                },
            )
            raise HTTPException(
                status_code=400,
                detail=f"图片大小超过限制，当前最大允许 {settings.max_upload_mb}MB",
            )

        validated_images.append((image_bytes, img.content_type, img.filename))

    logger.info(
        "start image analysis",
        extra={
            "request_id": request_id,
            "event": "image_analysis_started",
            "path": request.url.path,
            "upload_filename": [item[2] for item in validated_images],
            "content_type": [item[1] for item in validated_images],
            "size_bytes": [len(item[0]) for item in validated_images],
            "user_name": user_name,
            "scene_hint": scene_hint,
        },
    )

    async def run_single_image_analysis(
        image_bytes: bytes,
        content_type: str,
        filename: str,
    ) -> ImageAnalysisLiteResponse:
        logger.info(
            "single image analysis started",
            extra={
                "request_id": request_id,
                "event": "single_image_analysis_started",
                "path": request.url.path,
                "upload_filename": filename,
                "content_type": content_type,
                "user_name": user_name,
                "scene_hint": scene_hint,
            },
        )

        return await asyncio.to_thread(
            analyze_image_with_llm,
            image_bytes=image_bytes,
            content_type=content_type,
            request_id=request_id,
            user_name=user_name,
            scene_hint=scene_hint,
        )


    tasks = [
        run_single_image_analysis(image_bytes, content_type, filename)
        for image_bytes, content_type, filename in validated_images
    ]

    results = await asyncio.gather(*tasks)

    if len(results) == 1:
        result = results[0]
    else:
        result = aggregate_results(results)

# ------ stage 1: fallback result (optional) ------删除部分代码
#    if result.scene_type == "uncertain":
#            "image analysis returned fallback result",
#            extra={
#                "request_id": request_id,
#                "event": "image_analysis_fallback",
#                "path": request.url.path,
#                "warnings": result.warnings,
#            },
#        )

    logger.info(
        "image analysis completed",
        extra={
            "request_id": request_id,
            "event": "image_analysis_completed",
            "path": request.url.path,
#            "scene_type": result.scene_type,
            "confidence": result.confidence,
            "has_calories": result.calories is not None,
        },
    )

    return ImageAnalysisLiteResponse(
        request_id=request_id,
        confidence=result.confidence,
        calories=result.calories,
    )