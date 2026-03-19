import logging

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile

from app.core.config import settings
from app.core.security import verify_api_key
from app.schemas.image_analysis import ImageAnalysisResult
from app.services.image_chain import analyze_image_with_llm

router = APIRouter()
logger = logging.getLogger("uvicorn.error")


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
    if not image.filename:
        raise HTTPException(status_code=400, detail="未检测到上传文件")

    if image.content_type not in ["image/jpeg", "image/png", "image/webp"]:
        raise HTTPException(status_code=400, detail="不支持的图片类型")

    image_bytes = await image.read()
    if not image_bytes:
        raise HTTPException(status_code=400, detail="图片内容为空")

    max_upload_bytes = settings.max_upload_mb * 1024 * 1024
    if len(image_bytes) > max_upload_bytes:
        raise HTTPException(
            status_code=400,
            detail=f"图片大小超过限制，当前最大允许 {settings.max_upload_mb}MB",
        )

    request_id = request.state.request_id

    logger.info(
        "image analyze request received | request_id=%s | filename=%s | content_type=%s | size_bytes=%s | user_name=%s | scene_hint=%s",
        request_id,
        image.filename,
        image.content_type,
        len(image_bytes),
        user_name,
        scene_hint,
    )

    return analyze_image_with_llm(
        image_bytes=image_bytes,
        content_type=image.content_type,
        request_id=request_id,
        user_name=user_name,
        scene_hint=scene_hint,
    )