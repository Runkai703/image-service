# API_CONTRACT.md

## AI 图像分析微服务接口契约（Lite 版本）

---

## 1. 文档说明

本文档描述当前版本 AI 图像分析微服务的**真实接口行为（lite 模式）**。

* 当前版本：v1
* 模式：Lite（仅返回核心字段）
* 技术栈：FastAPI + LangChain + 通义千问多模态（qwen3-vl-flash）
* 鉴权方式：`X-API-Key`
* 请求追踪：`X-Request-Id`

---

## 2. 通用约定

### 2.1 鉴权

```http
X-API-Key: <your_token>
```

错误时返回：

```json
{
  "detail": "Invalid API key"
}
```

---

### 2.2 请求追踪

* Header：`X-Request-Id`
* Response Body：`request_id`

---

## 3. 接口列表

---

### 3.1 健康检查

**GET /**

```json
{
  "message": "AI Image Analysis Service is running",
  "env": "dev"
}
```

---

### 3.2 图片分析接口

**POST /v1/image/analyze**

Content-Type: `multipart/form-data`

---

## 4. 请求参数

### Headers

```http
X-API-Key: dev-token
```

---

### Form Data

| 字段         | 类型     | 必填 | 说明                |
| ---------- | ------ | -- | ----------------- |
| image      | file   | 否  | 单张图片              |
| images     | file[] | 否  | 多张图片              |
| user_name  | string | 否  | 用户名称              |
| scene_hint | string | 否  | 场景提示（meal / auto） |

---

### 图片约束

* 支持格式：JPEG / PNG / WEBP
* 建议数量：1–6 张
* 单张大小：由 `MAX_UPLOAD_MB` 控制

---

## 5. 成功响应（Lite）

```json
{
  "request_id": "img_xxxxx",
  "confidence": 0.87,
  "calories": 1580
}
```

---

### 字段说明

| 字段         | 类型     | 说明           |
| ---------- | ------ | ------------ |
| request_id | string | 请求唯一标识       |
| confidence | number | 模型整体置信度（0–1） |
| calories   | number | 所有图片合计热量     |

---

## 6. 错误响应

### 400 请求错误

```json
{
  "detail": "不支持的图片类型"
}
```

可能原因：

* 未上传图片
* 图片类型非法
* 图片为空
* 图片过大

---

### 401 未授权

```json
{
  "detail": "Invalid API key"
}
```

---

### 422 参数错误

```json
{
  "detail": [...]
}
```

---

### 500 服务异常

* 未处理异常
* 服务运行错误

---

## 7. 行为说明

### 7.1 多图处理方式

* 每张图片独立分析
* 服务端进行结果聚合
* 返回总 calories

---

### 7.2 返回特性

* 始终返回 lite 结构
* 不返回 foods / summary / health 信息

---

## 8. 调用建议

* 始终记录 `request_id`
* 不要假设失败一定返回 500
* 前端直接使用 `calories` 做展示

---

## 9. 未来扩展（非当前版本）

未来可能恢复：

* foods（食物识别）
* summary（描述）
* health_assessment（健康分析）

当前版本 **未开启**
