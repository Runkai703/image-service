# API_CONTRACT.md

## AI 图像分析微服务接口契约

## 1. 文档说明
本文档用于描述当前版本 **AI 图像分析微服务** 的真实接口行为，严格以当前代码实现为准。

- 服务名称：AI 图像分析微服务
- 当前版本：v1
- 技术栈：FastAPI + LangChain + 通义千问多模态（qwen3-vl-flash）
- 鉴权方式：`X-API-Key`
- 请求追踪：响应头 `X-Request-Id`

---

## 2. 通用约定

### 2.1 鉴权
除健康检查接口外，业务接口需要在请求头中携带：

```http
X-API-Key: <your_token>
```

未携带或不正确时，接口返回 `401 Unauthorized`。

---

### 2.2 请求追踪
每个请求都会自动生成一个 `request_id`：

- 响应头中返回：`X-Request-Id`
- 成功响应体中返回：`request_id`

示例：

```http
X-Request-Id: img_5d582dc0df17
```

---

### 2.3 响应格式约定
当前服务 **成功时直接返回业务对象本身**，也就是 `ImageAnalysisResult`，**没有** 外层统一包装：

```json
{
  "request_id": "img_xxxxx",
  "scene_type": "meal",
  "summary": "一碗牛肉冬瓜汤面",
  "confidence": 0.95,
  "foods": [],
  "glucose_meter": null,
  "phone_screen_glucose": null,
  "exercise": null,
  "health_assessment": null,
  "friendly_reply": "这是一碗营养较均衡的汤面。",
  "warnings": []
}
```

错误时使用 FastAPI 默认错误响应格式，通常为：

```json
{
  "detail": "不支持的图片类型"
}
```

---

## 3. 接口列表

### 3.1 健康检查接口
**Method**: `GET`  
**Path**: `/`

#### 请求示例
```bash
curl -i http://127.0.0.1:8000/
```

#### 成功响应示例
```json
{
  "message": "AI Image Analysis Service is running",
  "env": "dev"
}
```

#### 响应头示例
```http
X-Request-Id: img_xxxxx
```

---

### 3.2 图片分析接口
**Method**: `POST`  
**Path**: `/v1/image/analyze`  
**Content-Type**: `multipart/form-data`

#### 请求头
```http
X-API-Key: dev-token
```

#### 表单参数

| 字段名 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---:|---|---|
| image | file | 是 | - | 待分析图片 |
| user_name | string | 否 | 用户 | 用户名称 |
| scene_hint | string | 否 | auto | 场景提示，例如 `auto` / `meal` / `glucose` |

#### 图片要求

| 项目 | 说明 |
|---|---|
| 支持格式 | `image/jpeg`、`image/png`、`image/webp` |
| 大小限制 | 由环境变量 `MAX_UPLOAD_MB` 控制 |

#### 请求示例
```bash
curl -i -X POST "http://127.0.0.1:8000/v1/image/analyze"   -H "X-API-Key: dev-token"   -F "image=@test.jpg"   -F "user_name=Runkai"   -F "scene_hint=auto"
```

---

## 4. 成功响应结构

成功响应体为 `ImageAnalysisResult`：

| 字段名 | 类型 | 说明 |
|---|---|---|
| request_id | string | 请求唯一标识 |
| scene_type | string | 场景类型 |
| summary | string | 对图片内容的总结 |
| confidence | number | 模型整体置信度，范围通常为 0~1 |
| foods | array[FoodItem] | 食物识别结果 |
| glucose_meter | GlucoseReading \| null | 血糖仪识别结果 |
| phone_screen_glucose | GlucoseReading \| null | 手机截图中的血糖识别结果 |
| exercise | ExerciseInfo \| null | 运动识别结果 |
| health_assessment | HealthAssessment \| null | 健康分析结果 |
| friendly_reply | string | 面向用户的友好回复 |
| warnings | array[string] | 风险提示或告警信息 |

---

## 5. 子对象定义

### 5.1 FoodItem
| 字段名 | 类型 | 说明 |
|---|---|---|
| name | string | 食物名称 |
| portion | string | 份量描述 |
| confidence | number | 该食物识别置信度 |

#### 示例
```json
{
  "name": "牛肉",
  "portion": "中等块状，约4-5块",
  "confidence": 0.98
}
```

---

### 5.2 GlucoseReading
| 字段名 | 类型 | 说明 |
|---|---|---|
| reading | string | 血糖读数，如 `6.8` |
| unit | string | 单位，如 `mmol/L` |
| time | string \| null | 识别到的时间信息 |
| confidence | number | 识别置信度 |

#### 示例
```json
{
  "reading": "6.8",
  "unit": "mmol/L",
  "time": "07:42",
  "confidence": 0.94
}
```

---

### 5.3 ExerciseInfo
| 字段名 | 类型 | 说明 |
|---|---|---|
| type | string | 运动类型 |
| duration_minutes | integer \| null | 运动时长（分钟） |
| intensity | string | 强度，如 `low` / `medium` / `high` |
| confidence | number | 识别置信度 |

#### 示例
```json
{
  "type": "walking",
  "duration_minutes": 42,
  "intensity": "medium",
  "confidence": 0.91
}
```

---

### 5.4 HealthAssessment
| 字段名 | 类型 | 说明 |
|---|---|---|
| meal_balance | string | 饮食均衡度评价 |
| protein | string | 蛋白质评价 |
| fiber | string | 膳食纤维评价 |
| carb_risk | string | 碳水风险评价 |
| salt_risk | string | 盐分风险评价 |
| glucose_trend | string | 血糖趋势推断 |

#### 示例
```json
{
  "meal_balance": "均衡，富含蛋白质与蔬菜，碳水需注意",
  "protein": "高",
  "fiber": "高",
  "carb_risk": "中等",
  "salt_risk": "中等偏高",
  "glucose_trend": "平稳"
}
```

---

## 6. 场景类型说明（scene_type）

| 枚举值 | 说明 |
|---|---|
| meal | 饮食图片 |
| glucose_meter | 血糖仪读数图片 |
| phone_screen_glucose | 手机血糖截图 |
| exercise | 运动记录截图或照片 |
| mixed | 混合场景 |
| unclear | 图片内容不清晰 |
| uncertain | 模型兜底结果 / 无法可靠判断 |

---

## 7. 成功响应示例

### 7.1 饮食识别示例
```json
{
  "request_id": "img_5d582dc0df17",
  "scene_type": "meal",
  "summary": "一碗包含牛肉、冬瓜、青菜的热汤面，营养较均衡，适合日常饮食，但需注意汤中钠含量及面条碳水摄入量。",
  "confidence": 0.95,
  "foods": [
    {
      "name": "牛肉",
      "portion": "中等块状，约4-5块",
      "confidence": 0.98
    },
    {
      "name": "冬瓜",
      "portion": "大块，约2-3片",
      "confidence": 0.96
    },
    {
      "name": "青菜（白菜/生菜）",
      "portion": "叶菜类，约半颗",
      "confidence": 0.97
    },
    {
      "name": "汤底",
      "portion": "浓郁肉汤，含少量油花和碎料",
      "confidence": 0.90
    }
  ],
  "glucose_meter": null,
  "phone_screen_glucose": null,
  "exercise": null,
  "health_assessment": {
    "meal_balance": "均衡，富含蛋白质与蔬菜，碳水需注意",
    "protein": "高",
    "fiber": "高",
    "carb_risk": "中等",
    "salt_risk": "中等偏高（视汤底咸度）",
    "glucose_trend": "平稳"
  },
  "friendly_reply": "这是一碗营养丰富的牛肉冬瓜汤面，搭配青菜，汤底浓郁，适合补充能量和水分。如果正在控糖或关注血糖，建议注意汤中可能含有的淀粉或调味料影响，可适量减少面条摄入或选择粗粮面。",
  "warnings": []
}
```

---

## 8. 错误响应说明

### 8.1 401 未授权
适用场景：
- 缺少 `X-API-Key`
- `X-API-Key` 错误

#### 示例
```json
{
  "detail": "Invalid API key"
}
```

---

### 8.2 400 请求非法
适用场景：
- 未检测到上传文件
- 不支持的图片类型
- 图片内容为空
- 图片大小超过限制

#### 示例
```json
{
  "detail": "不支持的图片类型"
}
```

---

### 8.3 422 参数校验失败
适用场景：
- 请求表单格式不符合接口要求
- FastAPI 自动校验失败

#### 示例
```json
{
  "detail": [
    {
      "loc": ["body", "image"],
      "msg": "Field required",
      "type": "missing"
    }
  ]
}
```

---

### 8.4 500 服务端异常
适用场景：
- 未处理异常
- 服务启动配置异常
- 非预期运行时错误

#### 说明
需要注意：**模型调用失败或结构化解析失败时，服务层可能返回业务兜底结果，而不一定返回 500。**

也就是说，以下两种情况要区分：
1. **框架/服务本身异常**：可能返回 500
2. **模型调用失败但被业务代码兜底处理**：通常仍返回 200 + `scene_type="uncertain"` 的结构化结果

---

## 9. 模型兜底响应示例

当模型调用失败或结构化解析失败时，服务可能返回类似：

```json
{
  "request_id": "img_xxxxx",
  "scene_type": "uncertain",
  "summary": "暂时无法稳定完成图像分析，请稍后重试。",
  "confidence": 0.0,
  "foods": [],
  "glucose_meter": null,
  "phone_screen_glucose": null,
  "exercise": null,
  "health_assessment": null,
  "friendly_reply": "这次图片分析没有成功完成，你可以稍后重试，或换一张更清晰的图片。",
  "warnings": ["model_fallback"]
}
```

---

## 10. 集成建议

### 10.1 调用方应做的事情
- 始终保存 `request_id`
- 同时记录响应头中的 `X-Request-Id`
- 对 `scene_type="uncertain"` 做兜底处理
- 不要假设所有失败都会返回 500

### 10.2 前端 / Agent / Dify 集成建议
- 将 `friendly_reply` 直接给终端用户展示
- 将 `summary`、`foods`、`health_assessment` 用于结构化展示
- 将 `warnings` 用于内部风控或重试策略
