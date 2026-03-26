# AI Image Analysis Microservice

一个基于 FastAPI + 多模态大模型（qwen3-vl-flash）的图像分析微服务。

当前版本聚焦于：**饮食图片热量估算（calories estimation）**

---

## 🚀 Features

* 支持单张或多张图片上传
* 自动识别餐食并估算热量
* 多图逐张分析 + 服务端聚合
* 结构化 JSON 返回（lite 模式）
* API Key 鉴权
* request_id 全链路日志追踪

---

## 📌 Current Scope（当前能力范围）

当前版本只做一件事：

> **根据饮食图片估算总热量（calories）**

返回字段：

```json
{
  "request_id": "img_xxx",
  "confidence": 0.85,
  "calories": 1200
}
```

说明：

* `confidence`：模型置信度（0–1）
* `calories`：所有图片合计热量

---

## 🧠 Processing Flow

```text
Client
  ↓
FastAPI Router
  ↓
Image Input Processing（校验 / 读取）
  ↓
Image Service（多图并发调度）
  ↓
LLM（逐张图片分析）
  ↓
Aggregation（汇总 calories）
  ↓
Response（lite JSON）
```

---

## 📦 API Usage

### Endpoint

```http
POST /v1/image/analyze
```

---

### Headers

```http
X-API-Key: dev-token
```

---

### Request（多图）

```bash
curl -X POST "http://127.0.0.1:8000/v1/image/analyze" \
  -H "X-API-Key: dev-token" \
  -F "images=@meal1.jpg" \
  -F "images=@meal2.jpg" \
  -F "user_name=用户" \
  -F "scene_hint=meal"
```

---

### Request（单图）

```bash
curl -X POST "http://127.0.0.1:8000/v1/image/analyze" \
  -H "X-API-Key: dev-token" \
  -F "image=@meal.jpg"
```

---

### Response

```json
{
  "request_id": "img_abc123",
  "confidence": 0.87,
  "calories": 1580
}
```

---

## ⚙️ Tech Stack

* FastAPI
* LangChain
* 通义千问多模态（qwen3-vl-flash）
* asyncio 并发处理
* httpx

---

## 📁 Project Structure（简化）

```text
app/
  api/
    routes.py              # 接口层
  services/
    image_input.py         # 输入处理
    image_service.py       # 多图编排
    image_chain.py         # 模型调用
    aggregation.py         # 聚合逻辑
  schemas/
    image_analysis.py      # 数据结构
  core/
    config.py
    logging.py
    security.py
  main.py                  # 应用入口
```

---

## 🔐 Security

* API Key 鉴权（Header）
* 文件类型校验（JPEG / PNG / WEBP）
* 文件大小限制

---

## 📊 Logging

每个请求都有：

* `request_id`
* 全链路日志追踪
* 单图分析日志

---

## 🧩 Future Work（未来扩展）

* foods / 明细识别
* 营养结构分析
* 健康建议生成
* 用户数据存储
* RAG 健康知识库

---

## ✨ Summary

当前项目定位：

> 一个轻量、可扩展的 AI 图像分析微服务，专注饮食热量估算场景

---
