from langchain_openai import ChatOpenAI

from app.core.config import settings
from app.schemas.image_analysis import ImageAnalysisResult
from app.utils.file_utils import image_bytes_to_data_url


def analyze_image_with_llm(
    image_bytes: bytes,
    content_type: str,
    request_id: str,
    user_name: str = "用户",
    scene_hint: str = "auto",
) -> ImageAnalysisResult:
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

        structured_llm = llm.with_structured_output(ImageAnalysisResult)

        result = structured_llm.invoke(
            [
                {
                    "role": "system",
                    "content": """
你是一个图像分析助手，服务于健康客服系统。

你的任务：
1. 判断图片属于哪种场景：
   - meal_glucose
   - meal
   - exercise
   - poster
   - landscape
   - general
   - uncertain

2. 如果是餐饮/血糖图片：
   - 识别食物
   - 粗略判断搭配
   - 识别血糖仪读数
   - 识别手机屏幕中的血糖值（如果存在）
   - 给出简洁友好的分析

3. 如果是运动图片：
   - 识别运动类型，如跑步、骑行、健身房
   - 提取可见的时长、强度、配速、消耗等信息（如果可见）
   - 给出友好的运动建议

4. 如果是普通图片：
   - 做自然、友好的解释
   - 不要硬套健康分析

5. 如果图片信息不清楚：
   - scene_type 设为 uncertain
   - confidence 降低
   - 在 warnings 里说明原因
   - 不要编造读数

输出要求：
- 必须严格按 schema 输出
- confidence 取值 0 到 1
- 如果没有对应字段，填 null 或空数组
- 不要遗漏 request_id
""",
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": (
                                f"请分析这张图片并返回结构化结果。"
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

        if not result.friendly_reply:
            result.friendly_reply = (
                f"@{user_name}，我已经帮你看过这张图片了，下面是结构化分析结果。"
            )

        return result

    except Exception as e:
        return ImageAnalysisResult(
            request_id=request_id,
            scene_type="uncertain",
            summary="图片分析暂时未成功，已返回保底结果。",
            confidence=0.2,
            foods=[],
            glucose_meter=None,
            phone_screen_glucose=None,
            exercise=None,
            health_assessment=None,
            friendly_reply=(
                f"@{user_name}，这张图片我暂时没能稳定识别出来，"
                f"建议你换一张更清晰、主体更完整的图片再试一次。"
            ),
            warnings=[f"模型调用或结构化解析失败: {str(e)}"],
        )