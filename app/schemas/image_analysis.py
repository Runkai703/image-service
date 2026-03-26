from typing import Literal

from pydantic import BaseModel, Field


class FoodItem(BaseModel):
    name: str
    portion: str | None = None
    confidence: float | None = None


class GlucoseReading(BaseModel):
    reading: float | None = None
    unit: str | None = "mmol/L"
    time: str | None = None
    confidence: float | None = None


class ExerciseInfo(BaseModel):
    type: str | None = None
    duration_minutes: int | None = None
    intensity: Literal["low", "medium", "high"] | None = None
    confidence: float | None = None


class HealthAssessment(BaseModel):
    meal_balance: str | None = None
    protein: str | None = None
    fiber: str | None = None
    carb_risk: str | None = None
    salt_risk: str | None = None
    glucose_trend: str | None = None


class ImageAnalysisResult(BaseModel):
    request_id: str
    scene_type: Literal[
        "meal_glucose",
        "meal",
        "exercise",
        "poster",
        "landscape",
        "general",
        "uncertain",
    ]
    summary: str
    confidence: float = Field(ge=0.0, le=1.0)

    foods: list[FoodItem] = Field(default_factory=list)

    calories: int | None = Field(
        default=None,
        description="当为餐饮场景时，估算整餐总热量（单位 kcal）"
    )

    glucose_meter: GlucoseReading | None = None
    phone_screen_glucose: GlucoseReading | None = None
    exercise: ExerciseInfo | None = None
    health_assessment: HealthAssessment | None = None
    friendly_reply: str
    warnings: list[str] = Field(default_factory=list)

class ImageAnalysisLiteResponse(BaseModel):
    request_id: str
    confidence: float = Field(ge=0.0, le=1.0)
    calories: int | None = Field(
        default=None,
        description="多张饮食图片综合估算的总热量（单位 kcal）"
    )