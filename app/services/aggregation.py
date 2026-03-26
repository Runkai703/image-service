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