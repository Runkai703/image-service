# ====== DRAFT: full aggregation（旧版完整聚合，后续恢复时可用） ======
# 原来的 full aggregation 代码保留在这里
#from collections import Counter
#from app.schemas.image_analysis import ImageAnalysisResult
#
# def aggregate_results(results: list[ImageAnalysisResult]) -> ImageAnalysisResult:
#     if not results:
#         raise ValueError("results 不能为空")
#
#     if len(results) == 1:
#         return results[0]
#
#     base = results[0]
#
#     scene_type_counter = Counter(result.scene_type for result in results)
#     final_scene_type = scene_type_counter.most_common(1)[0][0]
#
#     merged_foods = []
#     merged_warnings = []
    #total_calories = 0
    #has_any_calories = False
    #
    #confidence_sum = 0.0
    #
    #final_glucose_meter = None
    #final_phone_screen_glucose = None
    #final_exercise = None
    #final_health_assessment = None
    #
    #for result in results:
    #    confidence_sum += result.confidence
    #
    #    if result.foods:
    #        merged_foods.extend(result.foods)
    #
    #    if result.warnings:
    #        merged_warnings.extend(result.warnings)
    #
    #    if result.calories is not None:
    #        total_calories += result.calories
    #        has_any_calories = True
    #
    #    if final_glucose_meter is None and result.glucose_meter is not None:
    #        final_glucose_meter = result.glucose_meter
    #
    #    if (
    #        final_phone_screen_glucose is None
    #        and result.phone_screen_glucose is not None
    #    ):
    #        final_phone_screen_glucose = result.phone_screen_glucose
    #
    #    if final_exercise is None and result.exercise is not None:
    #        final_exercise = result.exercise
    #
    #    if final_health_assessment is None and result.health_assessment is not None:
    #        final_health_assessment = result.health_assessment
    #
    #avg_confidence = round(confidence_sum / len(results), 3)
    #
    #return ImageAnalysisResult(
    #    request_id=base.request_id,
    #    scene_type=final_scene_type,
    #    summary=base.summary,
    #    confidence=avg_confidence,
    #    foods=merged_foods,
    #    calories=total_calories if has_any_calories else None,
    #    glucose_meter=final_glucose_meter,
    #    phone_screen_glucose=final_phone_screen_glucose,
    #    exercise=final_exercise,
    #    health_assessment=final_health_assessment,
    #    friendly_reply=base.friendly_reply,
    #    warnings=merged_warnings,
    #)
#
# ====== CURRENT: lite aggregation（当前阶段：仅聚合 request_id / confidence / calories） ======
from app.schemas.image_analysis import ImageAnalysisLiteResponse


def aggregate_results(
    results: list[ImageAnalysisLiteResponse],
) -> ImageAnalysisLiteResponse:
    if not results:
        raise ValueError("results 不能为空")

    if len(results) == 1:
        return results[0]

    base = results[0]

    total_confidence = sum(result.confidence for result in results)
    avg_confidence = round(total_confidence / len(results), 3)

    calorie_values = [result.calories for result in results if result.calories is not None]
    total_calories = sum(calorie_values) if calorie_values else None

    return ImageAnalysisLiteResponse(
        request_id=base.request_id,
        confidence=avg_confidence,
        calories=total_calories,
    )