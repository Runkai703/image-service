import uuid

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.core.config import settings
from app.schemas.image_analysis import ImageAnalysisResult
from app.services.image_chain import analyze_image_with_llm

router = APIRouter()


@router.post("/v1/image/analyze", response_model=ImageAnalysisResult)
async def analyze_image(
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

    request_id = f"img_{uuid.uuid4().hex[:12]}"

    return analyze_image_with_llm(
        image_bytes=image_bytes,
        content_type=image.content_type,
        request_id=request_id,
        user_name=user_name,
        scene_hint=scene_hint,
    )