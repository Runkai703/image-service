import asyncio
import logging
from typing import List

from app.schemas.image_analysis import ImageAnalysisLiteResponse
from app.services.aggregation import aggregate_results
from app.services.image_chain import analyze_image_with_llm
from app.services.image_input import PreparedImage

logger = logging.getLogger("app.image")


async def analyze_images(
    *,
    images: List[PreparedImage],
    request_id: str,
    user_name: str,
    scene_hint: str,
) -> ImageAnalysisLiteResponse:
    """
    多图分析业务编排层：
    - 并发执行单图分析
    - 聚合结果
    """

    async def run_single_image_analysis(image: PreparedImage):
        logger.info(
            "single image analysis started",
            extra={
                "request_id": request_id,
                "event": "single_image_analysis_started",
                "upload_filename": image.filename,
                "content_type": image.content_type,
            },
        )

        return await asyncio.to_thread(
            analyze_image_with_llm,
            image_bytes=image.image_bytes,
            content_type=image.content_type,
            request_id=request_id,
            user_name=user_name,
            scene_hint=scene_hint,
        )

    tasks = [run_single_image_analysis(img) for img in images]

    results = await asyncio.gather(*tasks)

    if len(results) == 1:
        return results[0]

    return aggregate_results(results)