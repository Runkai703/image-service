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
