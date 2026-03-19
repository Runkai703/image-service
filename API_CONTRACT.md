# API CONTRACT

AI Image Analysis Service 接口契约文档

版本：v1.0  
基础路径：`/v1`

---

## 1. 通用约定

### 1.1 响应格式

所有接口统一返回 JSON：

```json
{
  "request_id": "string",
  "success": true,
  "message": "string",
  "data": {}
}
```

字段说明：

| 字段 | 类型 | 说明 |
|------|------|------|
| request_id | string | 请求唯一 ID |
| success | boolean | 是否成功 |
| message | string | 提示信息 |
| data | object | 实际返回数据 |

---

### 1.2 错误码（基础）

| HTTP Code | 含义 |
|----------|------|
| 200 | 成功 |
| 400 | 参数错误 |
| 413 | 文件过大 |
| 415 | 不支持的文件类型 |
| 500 | 服务内部错误 |

---

## 2. 图片分析接口

### 2.1 接口说明

分析用户上传图片，并返回结构化健康/内容分析结果。

### 2.2 请求

#### URL

`POST /v1/image/analyze`

#### Content-Type

`multipart/form-data`

#### 参数

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| image | file | 是 | 图片文件 |
| user_name | string | 否 | 用户名（用于生成回复） |
| scene_hint | string | 否 | 场景提示（默认 auto） |

### 2.3 请求示例

```bash
curl -X POST "http://127.0.0.1:8000/v1/image/analyze" \
  -H "accept: application/json" \
  -F "image=@test.jpg" \
  -F "user_name=Runkai" \
  -F "scene_hint=auto"
```

### 2.4 成功响应

```json
{
  "request_id": "img_123456abcdef",
  "success": true,
  "message": "ok",
  "data": {
    "scene_type": "meal",
    "summary": "这是一张餐食图片",
    "confidence": 0.91,
    "foods": [],
    "glucose_meter": null,
    "phone_screen_glucose": null,
    "exercise": null,
    "health_assessment": {},
    "friendly_reply": "",
    "warnings": []
  }
}
```

### 2.5 data 字段说明

#### scene_type

| 值 | 含义 |
|----|------|
| meal_glucose | 餐食 + 血糖 |
| meal | 餐食 |
| exercise | 运动 |
| poster | 海报/宣传图 |
| landscape | 风景 |
| general | 通用图片 |
| uncertain | 不确定 |

#### foods（餐食识别）

```json
[
  {
    "name": "米饭",
    "portion": "1碗",
    "confidence": 0.95
  }
]
```

#### glucose_meter（血糖仪）

```json
{
  "value": 6.5,
  "unit": "mmol/L",
  "time": "08:30"
}
```

#### phone_screen_glucose（App 截图）

```json
{
  "value": 7.2,
  "trend": "上升",
  "time": "餐后"
}
```

#### exercise（运动）

```json
{
  "type": "跑步",
  "duration": "30分钟",
  "intensity": "中等"
}
```

#### health_assessment（健康分析）

```json
{
  "meal_balance": "",
  "protein": "",
  "fiber": "",
  "carb_risk": "",
  "salt_risk": "",
  "glucose_trend": ""
}
```

#### friendly_reply

用于直接返回给用户的自然语言回复。

#### warnings

```json
[
  "图片清晰度较低",
  "识别结果可能不准确"
]
```

---

## 3. 失败响应示例

### 3.1 参数错误

```json
{
  "request_id": "xxx",
  "success": false,
  "message": "No file uploaded",
  "data": null
}
```

### 3.2 文件类型错误

```json
{
  "request_id": "xxx",
  "success": false,
  "message": "Unsupported file type",
  "data": null
}
```

### 3.3 文件过大

```json
{
  "request_id": "xxx",
  "success": false,
  "message": "File too large",
  "data": null
}
```

### 3.4 模型失败兜底

```json
{
  "request_id": "xxx",
  "success": true,
  "message": "fallback result",
  "data": {
    "scene_type": "uncertain",
    "summary": "暂时无法准确识别该图片",
    "confidence": 0.3
  }
}
```

---

## 4. 后续扩展（预留）

未来接口扩展方向：

- `/v1/image/batch_analyze`
- `/v1/image/ocr`
- `/v1/health/chat`
- `/v1/user/profile`

---

## 5. 版本说明

| 版本 | 时间 | 说明 |
|------|------|------|
| v1.0 | 当前 | 初始版本 |
