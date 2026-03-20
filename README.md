# AI 图像分析微服务

## 项目简介
这是一个基于 FastAPI + LangChain + 通义千问多模态模型（qwen3-vl-flash）的 AI 图像分析微服务。

用户上传图片后，服务会返回结构化 JSON，用于健康分析（饮食、血糖、运动等场景）。

---

## 核心功能
- 图片分析接口：POST /v1/image/analyze
- 健康检查接口：GET /
- API Key 鉴权（Header: X-API-Key）
- 自动生成 request_id（全链路追踪）
- 响应头返回 X-Request-Id
- 结构化 JSON 输出（Pydantic Schema）
- 图片类型与大小校验
- 模型异常时返回兜底结果（不会直接崩溃）
- 支持 Docker 部署

---

## 技术栈
- FastAPI
- LangChain
- 通义千问（DashScope）
- Docker

---

## 项目结构
```
app/
  api/        # 路由层
  core/       # 配置、鉴权、日志
  schemas/    # 数据结构定义
  services/   # 业务逻辑（模型调用）
```

---

## 环境变量配置

复制 `.env.example` 为 `.env` 并填写：

- DASHSCOPE_API_KEY=你的API Key
- QWEN_MODEL=qwen3-vl-flash
- API_AUTH_TOKEN=dev-token
- MAX_UPLOAD_MB=5
- APP_ENV=dev

---

## 本地运行

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

---

## API 调用示例

### 1. 健康检查
```bash
curl -i http://127.0.0.1:8000/
```

---

### 2. 图片分析接口
```bash
curl -i -X POST "http://127.0.0.1:8000/v1/image/analyze"   -H "X-API-Key: dev-token"   -F "image=@test.jpg"   -F "user_name=用户"   -F "scene_hint=auto"
```

---

## 返回说明

### 响应头
- X-Request-Id：请求唯一标识（用于日志追踪）

### 响应体
返回结构化 JSON，例如：

```json
{
  "request_id": "img_xxxxx",
  "scene_type": "meal",
  "summary": "...",
  "confidence": 0.95,
  "foods": [...],
  "health_assessment": {...},
  "friendly_reply": "..."
}
```

---

## 注意事项
- 支持图片格式：jpeg / png / webp
- 图片大小限制由 MAX_UPLOAD_MB 控制
- 必须携带 Header：X-API-Key
- 模型调用失败时不会返回 500，而是返回兜底结构化结果
- 当前仅支持单张图片分析

---

## 后续规划
- RAG 知识库接入
- 用户数据存储（SQL）
- 图片自动压缩与预处理
- 日志结构化（JSON Log）
- 接入监控系统（ELK / Loki）
