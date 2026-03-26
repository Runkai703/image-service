from dataclasses import dataclass

from fastapi import HTTPException, UploadFile

from app.core.config import settings


ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}


@dataclass
class PreparedImage:
    filename: str
    content_type: str
    image_bytes: bytes


async def prepare_uploaded_images(
    *,
    images: list[UploadFile] | None,
    image: UploadFile | None,
) -> list[PreparedImage]:
    """
    统一兼容单图 / 多图输入，并完成文件读取与基础校验。
    """

    final_images: list[UploadFile] = []

    if images:
        final_images.extend(images)

    if image:
        final_images.append(image)

    if not final_images:
        raise HTTPException(status_code=400, detail="未检测到上传文件")

    prepared_images: list[PreparedImage] = []
    max_upload_bytes = settings.max_upload_mb * 1024 * 1024

    for img in final_images:
        if not img.filename:
            raise HTTPException(status_code=400, detail="未检测到上传文件名")

        if img.content_type not in ALLOWED_IMAGE_TYPES:
            raise HTTPException(status_code=400, detail="不支持的图片类型")

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
                content_type=img.content_type,
                image_bytes=image_bytes,
            )
        )

    return prepared_images