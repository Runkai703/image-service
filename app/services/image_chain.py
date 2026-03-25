import logging

from langchain_openai import ChatOpenAI

from app.core.config import settings
from app.schemas.image_analysis import ImageAnalysisLiteResponse
from app.utils.file_utils import image_bytes_to_data_url

logger = logging.getLogger("app.image_chain")


def analyze_image_with_llm(
    image_bytes: bytes,
    content_type: str,
    request_id: str,
    user_name: str = "用户",
    scene_hint: str = "auto",
) -> ImageAnalysisLiteResponse:
    try:
        data_url = image_bytes_to_data_url(
            image_bytes=image_bytes,
            content_type=content_type,
        )

        llm = ChatOpenAI(
            model=settings.qwen_model,
            temperature=0,
            api_key=settings.dashscope_api_key,
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        )

        structured_llm = llm.with_structured_output(ImageAnalysisLiteResponse)

        result = structured_llm.invoke(
            [
                {
                    "role": "system",
                    "content": """
你是一个饮食图片热量估算助手。

当前输入一定是饮食图片。
请只完成以下任务：
1. 估算这张图片中食物的总热量 calories（单位 kcal，整数）
2. 给出整体置信度 confidence（0 到 1）
3. 返回 request_id

输出要求：
- 必须严格按 schema 输出
- request_id 不要遗漏
- confidence 取值 0 到 1
- calories 必须为整数；如果实在无法判断则填 null
- 不要输出任何 schema 之外的内容
""",
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": (
                                f"请分析这张饮食图片并返回结构化结果。"
                                f"request_id={request_id}; "
                                f"user_name={user_name}; "
                                f"scene_hint={scene_hint}"
                            ),
                        },
                        {
                            "type": "image_url",
                            "image_url": {"url": data_url},
                        },
                    ],
                },
            ]
        )

        if not result.request_id:
            result.request_id = request_id

        return result

    except Exception as e:
        logger.exception(
            "image structured output failed",
            extra={
                "request_id": request_id,
                "event": "image_structured_output_failed",
                "content_type": content_type,
                "reason": str(e),
            },
        )

        # ====== DRAFT: full schema fallback（完整能力保留，后续可恢复） ======
        # return ImageAnalysisResult(
        #     request_id=request_id,
        #     scene_type="uncertain",
        #     summary="图片分析暂时未成功，已返回保底结果。",
        #     confidence=0.2,
        #     foods=[],
        #     glucose_meter=None,
        #     phone_screen_glucose=None,
        #     exercise=None,
        #     health_assessment=None,
        #     friendly_reply=(
        #         f"@{user_name}，这张图片我暂时没能稳定识别出来，"
        #         f"建议你换一张更清晰、主体更完整的图片再试一次。"
        #     ),
        #     warnings=[f"模型调用或结构化解析失败: {str(e)}"],
        # )

        # ====== CURRENT: lite fallback（当前阶段使用） ======
        return ImageAnalysisLiteResponse(
            request_id=request_id,
            confidence=0.2,
            calories=None,
        )