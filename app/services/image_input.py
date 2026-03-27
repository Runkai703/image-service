from dataclasses import dataclass
from pathlib import Path

from fastapi import HTTPException, UploadFile

from app.core.config import settings


ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}
ALLOWED_IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp"}


@dataclass
class PreparedImage:
    filename: str
    content_type: str
    image_bytes: bytes


def _is_allowed_image(img: UploadFile) -> bool:
    """
    优先按 content_type 校验。
    对 Windows curl 这类会把图片发成 application/octet-stream 的情况，
    回退按文件扩展名校验。
    """
    if img.content_type in ALLOWED_IMAGE_TYPES:
        return True

    if img.content_type == "application/octet-stream":
        suffix = Path(img.filename or "").suffix.lower()
        if suffix in ALLOWED_IMAGE_SUFFIXES:
            return True

    return False


async def prepare_uploaded_images(
    *,
    images: list[UploadFile],
) -> list[PreparedImage]:
    """
    统一处理上传图片，并完成文件读取与基础校验。
    单图和多图都通过 images 字段传入。
    """

    if not images:
        raise HTTPException(status_code=400, detail="未检测到上传文件")

    prepared_images: list[PreparedImage] = []
    max_upload_bytes = settings.max_upload_mb * 1024 * 1024

    for img in images:
        if not img.filename:
            raise HTTPException(status_code=400, detail="未检测到上传文件名")

        if not _is_allowed_image(img):
            raise HTTPException(
                status_code=400,
                detail=f"不支持的图片类型: {img.content_type}"
            )

        image_bytes = await img.read()

        if not image_bytes:
            raise HTTPException(status_code=400, detail="图片内容为空")

        if len(image_bytes) > max_upload_bytes:
            raise HTTPException(
                status_code=400,
                detail=f"图片大小超过限制，当前最大允许 {settings.max_upload_mb}MB",
            )

        prepared_images.append(
            PreparedImage(
                filename=img.filename,
                content_type=img.content_type or "application/octet-stream",
                image_bytes=image_bytes,
            )
        )

    return prepared_images