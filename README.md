# image-service

A multimodal image analysis micro-service built with **FastAPI + LangChain + Qwen (DashScope compatible API)**.

这个项目用于接收用户上传图片，调用多模态模型进行分析，并返回统一的结构化 JSON 结果。当前定位适合接入健康客服、Agent 工作流、Dify、企业微信后端等场景。

---

## Current Capabilities

当前已实现：

- FastAPI 微服务
- 图片分析接口：`POST /v1/image/analyze`
- 支持图片上传（multipart/form-data）
- 接入通义千问多模态模型：`qwen3-vl-flash`
- 使用 LangChain 结构化输出
- 返回统一的 Pydantic JSON Schema
- 自动生成 `request_id`
- 文件类型校验
- 文件大小限制
- 模型调用失败时返回兜底结果

---

## Tech Stack

- Python
- FastAPI
- LangChain
- langchain-openai
- Qwen3-VL-Flash
- DashScope OpenAI-compatible API
- Pydantic / pydantic-settings

---

## Project Structure

```bash
.
├── app
│   ├── api
│   │   └── routes.py
│   ├── core
│   │   ├── config.py
│   │   └── logging.py
│   ├── schemas
│   │   └── image_analysis.py
│   ├── services
│   │   ├── image_chain.py
│   │   └── image_preprocess.py
│   ├── utils
│   │   └── file_utils.py
│   ├── __init__.py
│   └── main.py
├── tests
│   └── __init__.py
├── .env.example
├── API_CONTRACT.md
├── Dockerfile
├── PROJECT_BRIEF.md
├── README.md
└── requirements.txt
```

---

## API Overview

### 1) Health Check

#### GET `/`

返回服务基础状态。

**Response Example**

```json
{
  "message": "image-service is running",
  "env": "dev"
}
```

---

### 2) Analyze Image

#### POST `/v1/image/analyze`

上传图片并返回结构化分析结果。

### Request

`Content-Type: multipart/form-data`

字段：

- `image`: 图片文件，必填
- `user_name`: 用户名，可选，默认 `"用户"`
- `scene_hint`: 场景提示，可选，默认 `"auto"`

支持的图片类型：

- `image/jpeg`
- `image/png`
- `image/webp`

---

## cURL Example

```bash
curl -X POST "http://127.0.0.1:8000/v1/image/analyze"   -H "accept: application/json"   -F "image=@test.jpg"   -F "user_name=Runkai"   -F "scene_hint=auto"
```

---

## Response Schema

当前结构化返回核心字段包括：

- `request_id`
- `scene_type`
- `summary`
- `confidence`
- `foods`
- `glucose_meter`
- `phone_screen_glucose`
- `exercise`
- `health_assessment`
- `friendly_reply`
- `warnings`

### Supported scene_type

当前代码支持的场景类型为：

- `meal_glucose`
- `meal`
- `exercise`
- `poster`
- `landscape`
- `general`
- `uncertain`

---

## Response Example

```json
{
  "request_id": "img_123456abcdef",
  "scene_type": "meal",
  "summary": "这是一张餐食图片，包含主食、蛋白质和蔬菜。",
  "confidence": 0.91,
  "foods": [
    {
      "name": "米饭",
      "portion": "1小碗",
      "confidence": 0.95
    },
    {
      "name": "鸡肉",
      "portion": "1份",
      "confidence": 0.88
    }
  ],
  "glucose_meter": null,
  "phone_screen_glucose": null,
  "exercise": null,
  "health_assessment": {
    "meal_balance": "整体搭配较均衡",
    "protein": "有一定蛋白质来源",
    "fiber": "蔬菜量中等",
    "carb_risk": "主食存在一定碳水负荷",
    "salt_risk": null,
    "glucose_trend": null
  },
  "friendly_reply": "@Runkai，我已经帮你看过这张图片了，下面是结构化分析结果。",
  "warnings": []
}
```

---

## Local Development

### 1. Clone repository

```bash
git clone git@github.com:Runkai703/image-service.git
cd image-service
git checkout feature/init-project
```

### 2. Create virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Windows:

```bash
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## Environment Variables

先复制示例文件：

```bash
cp .env.example .env
```

然后把 `.env` 改成下面这种形式：

```env
APP_NAME=image-service
APP_ENV=dev
APP_HOST=0.0.0.0
APP_PORT=8000
LOG_LEVEL=INFO

DASHSCOPE_API_KEY=your_dashscope_api_key_here
QWEN_MODEL=qwen3-vl-flash

API_AUTH_TOKEN=dev-token
MAX_UPLOAD_MB=10
```

---

## Run the Service

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

启动后可访问：

- Service: `http://127.0.0.1:8000`
- Swagger: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

---

## Error Handling

当前接口已包含这些基础校验与兜底：

- 未上传文件
- 文件内容为空
- 不支持的图片格式
- 图片超出大小限制
- 模型调用失败
- 结构化解析失败时返回保底 JSON

---

## Notes

当前项目里已经存在但尚未完善的内容：

- `README.md`：待补充
- `API_CONTRACT.md`：待补充
- `Dockerfile`：待补充
- `tests/`：测试用例待补充
- `image_preprocess.py`：目前基本还未使用/内容为空

---

## License

MIT
