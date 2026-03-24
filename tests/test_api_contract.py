from fastapi.testclient import TestClient

from app.main import app
from app.core.config import settings
from app.schemas.image_analysis import ImageAnalysisResult


client = TestClient(app)


def _auth_headers() -> dict:
    return {"X-API-Key": settings.api_auth_token}


def _fake_success_result(request_id: str) -> ImageAnalysisResult:
    return ImageAnalysisResult(
        request_id=request_id,
        scene_type="meal",
        summary="这是一张测试餐食图片",
        confidence=0.95,
        foods=[
            {
                "name": "米饭",
                "portion": "1碗",
                "confidence": 0.98,
            }
        ],
        calories=520,
        glucose_meter=None,
        phone_screen_glucose=None,
        exercise=None,
        health_assessment={
            "meal_balance": "较均衡",
            "protein": "一般",
            "fiber": "一般",
            "carb_risk": "中等",
            "salt_risk": None,
            "glucose_trend": None,
        },
        friendly_reply="测试返回成功",
        warnings=[],
    )


def test_root_healthcheck():
    response = client.get("/")

    assert response.status_code == 200
    body = response.json()
    assert "message" in body
    assert "env" in body
    assert "X-Request-Id" in response.headers


def test_analyze_image_success(monkeypatch):
    def fake_analyze_image_with_llm(
        image_bytes: bytes,
        content_type: str,
        request_id: str,
        user_name: str = "用户",
        scene_hint: str = "auto",
    ) -> ImageAnalysisResult:
        assert isinstance(image_bytes, bytes)
        assert content_type == "image/jpeg"
        assert user_name == "Runkai"
        assert scene_hint == "meal"
        return _fake_success_result(request_id=request_id)

    monkeypatch.setattr(
        "app.api.routes.analyze_image_with_llm",
        fake_analyze_image_with_llm,
    )

    files = {"image": ("test.jpg", b"fake-jpeg-bytes", "image/jpeg")}
    data = {"user_name": "Runkai", "scene_hint": "meal"}

    response = client.post(
        "/v1/image/analyze",
        headers=_auth_headers(),
        files=files,
        data=data,
    )

    assert response.status_code == 200
    assert "X-Request-Id" in response.headers

    body = response.json()
    assert body["request_id"] == response.headers["X-Request-Id"]
    assert body["scene_type"] == "meal"
    assert body["summary"] == "这是一张测试餐食图片"
    assert body["friendly_reply"] == "测试返回成功"
    assert body["calories"] == 520
    assert isinstance(body["foods"], list)


def test_analyze_image_unauthorized():
    files = {"image": ("test.jpg", b"fake-jpeg-bytes", "image/jpeg")}

    response = client.post("/v1/image/analyze", files=files)

    assert response.status_code == 401
    assert "X-Request-Id" in response.headers


def test_analyze_image_unsupported_content_type():
    files = {"image": ("test.txt", b"hello", "text/plain")}

    response = client.post(
        "/v1/image/analyze",
        headers=_auth_headers(),
        files=files,
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "不支持的图片类型"
    assert "X-Request-Id" in response.headers


def test_analyze_image_empty_file():
    files = {"image": ("empty.jpg", b"", "image/jpeg")}

    response = client.post(
        "/v1/image/analyze",
        headers=_auth_headers(),
        files=files,
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "图片内容为空"
    assert "X-Request-Id" in response.headers


def test_analyze_image_file_too_large():
    original_max_upload_mb = settings.max_upload_mb
    settings.max_upload_mb = 1

    try:
        big_content = b"a" * (1024 * 1024 + 1)
        files = {"image": ("big.jpg", big_content, "image/jpeg")}

        response = client.post(
            "/v1/image/analyze",
            headers=_auth_headers(),
            files=files,
        )

        assert response.status_code == 400
        assert response.json()["detail"] == "图片大小超过限制，当前最大允许 1MB"
        assert "X-Request-Id" in response.headers
    finally:
        settings.max_upload_mb = original_max_upload_mb


def test_analyze_image_fallback_result(monkeypatch):
    def fake_analyze_image_with_llm(
        image_bytes: bytes,
        content_type: str,
        request_id: str,
        user_name: str = "用户",
        scene_hint: str = "auto",
    ) -> ImageAnalysisResult:
        return ImageAnalysisResult(
            request_id=request_id,
            scene_type="uncertain",
            summary="暂时无法稳定完成图像分析，请稍后重试。",
            confidence=0.0,
            foods=[],
            calories=None,
            glucose_meter=None,
            phone_screen_glucose=None,
            exercise=None,
            health_assessment=None,
            friendly_reply="这次图片分析没有成功完成，你可以稍后重试。",
            warnings=["model_fallback"],
        )

    monkeypatch.setattr(
        "app.api.routes.analyze_image_with_llm",
        fake_analyze_image_with_llm,
    )

    files = {"image": ("test.jpg", b"fake-jpeg-bytes", "image/jpeg")}

    response = client.post(
        "/v1/image/analyze",
        headers=_auth_headers(),
        files=files,
    )

    assert response.status_code == 200
    body = response.json()
    assert body["scene_type"] == "uncertain"
    assert body["request_id"] == response.headers["X-Request-Id"]
    assert body["warnings"] == ["model_fallback"]