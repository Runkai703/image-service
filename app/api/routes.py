import logging
from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile

from app.core.security import verify_api_key
from app.schemas.image_analysis import ImageAnalysisLiteResponse
from app.services.image_input import prepare_uploaded_images
from app.services.image_service import analyze_images

router = APIRouter()
logger = logging.getLogger("app.image")


@router.post(
    "/v1/image/analyze",
    response_model=ImageAnalysisLiteResponse,
    dependencies=[Depends(verify_api_key)],
)
async def analyze_image(
    request: Request,
    images: Annotated[
        list[UploadFile],
        File(..., description="上传单张或多张饮食图片"),
    ],
    user_name: str = Form("用户"),
    scene_hint: str = Form("auto"),
) -> ImageAnalysisLiteResponse:
    request_id = request.state.request_id

    logger.info(
        "image analyze request received",
        extra={
            "request_id": request_id,
            "event": "image_analyze_request_received",
            "path": request.url.path,
            "upload_filename": [img.filename for img in images],
            "content_type": [img.content_type for img in images],
            "user_name": user_name,
            "scene_hint": scene_hint,
        },
    )

    try:
        prepared_images = await prepare_uploaded_images(images=images)
    except HTTPException as e:
        logger.warning(
            "image validation failed",
            extra={
                "request_id": request_id,
                "event": "image_validation_failed",
                "path": request.url.path,
                "reason": e.detail,
            },
        )
        raise

    logger.info(
        "start image analysis",
        extra={
            "request_id": request_id,
            "event": "image_analysis_started",
            "path": request.url.path,
            "upload_filename": [item.filename for item in prepared_images],
            "content_type": [item.content_type for item in prepared_images],
            "size_bytes": [len(item.image_bytes) for item in prepared_images],
            "user_name": user_name,
            "scene_hint": scene_hint,
        },
    )

    result = await analyze_images(
        images=prepared_images,
        request_id=request_id,
        user_name=user_name,
        scene_hint=scene_hint,
    )

    logger.info(
        "image analysis completed",
        extra={
            "request_id": request_id,
            "event": "image_analysis_completed",
            "path": request.url.path,
            "confidence": result.confidence,
            "has_calories": result.calories is not None,
        },
    )

    return ImageAnalysisLiteResponse(
        request_id=request_id,
        confidence=result.confidence,
        calories=result.calories,
    )