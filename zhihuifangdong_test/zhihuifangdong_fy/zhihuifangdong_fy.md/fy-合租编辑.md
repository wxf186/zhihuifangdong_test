

# 协议分析报告：合租房源编辑操作

## 1. 场景识别

**操作类型**：房源户型编辑（合租房屋多房间配置）

**业务描述**：用户在长租公寓管理平台（端口 8084）上编辑合租房源的户型信息，包括设置房间数量、租金、付款方式、押付规则等参数，并保存至服务端。

---

## 2. 交互流程概述

| 阶段 | 描述 |
|------|------|
| **阶段1：初始化** | 前端页面加载，从 URL 参数中解析 `communityId`、`parentId`、`meterSplitWayValue` 等配置 |
| **阶段2：数据预填** | 调用 `cotenancyHouseAddEditMore` 获取现有户型数据，回填表单 |
| **阶段3：配置修改** | 用户修改户型参数（室/厅/卫/厨数量、付款方式、押金月数、各房间租金） |
| **阶段4：提交保存** | 调用 `cotenancyHouseEdit` API 提交编辑数据 |
| **阶段5：状态验证** | 调用 `checkHouseIndexPlus` 验证房源索引状态 |
| **阶段6：刷新列表** | 调用 `wholeHouse/list` 更新房源列表显示 |

**用户行为链**：
```
进入页面 → 修改房间配置 → 填写租金 → 选择押付方式 → 点击"完成" → 保存成功 → 刷新列表
```

---

## 3. API 端点清单

### 3.1 核心业务 API

| # | 方法 | 路径 | 用途 | 关键参数 |
|---|------|------|------|---------|
| 1 | **POST** | `/core/houseAdd/cotenancyHouseEdit` | 编辑/保存合租户型 | `parentId`、`house[]`、支付规则 |
| 2 | **GET** | `/core/app/house/cotenancyHouseAddEditMore` | 获取户型详情（前端主动调用） | `id`（parentId） |
| 3 | **POST** | `/core/wholeHouse/list` | 查询整房列表 | 分页参数 |
| 4 | **POST** | `/core/checkHouseIndexPlus` | 检查房源索引状态 | 表单编码参数 |

### 3.2 请求体详解

**cotenancyHouseEdit** 请求体结构：

```json
{
  "parentId": 1558024,              // 父房源ID
  "house": [                         // 房间数组
    {
      "houseId": 0,                  // 0表示新增
      "name": "1室",                 // 房间名称
      "rent": "333",                 // 月租金
      "houseStatus": {"name": "WAITING_RENT"},  // 待租状态
      "meterArr": [],                // 电表配置
      "doorLockArr": [],             // 门锁配置
      "waterArr": [],                // 水表配置
      "meterAllocationProportion": 1, // 电费分摊比例
      "waterAllocationProportion": 1, // 水费分摊比例
      "isEdit": true,
      "add": true
    },
    {
      "houseId": 0,
      "name": "2室",
      "rent": "444",
      "houseStatus": {"name": "WAITING_RENT"},
      "meterAllocationProportion": 1,
      "waterAllocationProportion": 1,
      "isEdit": true,
      "add": true
    }
  ],
  "kitchenNumber": 1,                // 厨房数
  "livingRoomNumber": 1,             // 客厅数
  "roomNumber": 2,                   // 卧室数
  "toiletNumber": 1,                 // 卫生间数
  "payMethod": "MONTH_PAY",          // 付款方式（月付）
  "pledgeCount": 1,                  // 押金月数
  "perMonth": 1                      // 付款月数
}
```

**响应**：
```json
{
  "success": true,
  "message": "成功"
}
```

---

## 4. 鉴权机制分析

### 4.1 认证方式

| 项目 | 详情 |
|------|------|
| **认证类型** | Bearer Token（JWT） |
| **Header 字段** | `Authorization: Bearer <token>` |
| **Token 来源** | 用户登录后由服务端签发，客户端存储于内存/Storage |

### 4.2 JWT Token 解析

```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.
eyJwYXNzd29yZCI6IjU2OTBkZGRmYTI4YWUwODVkMjM1MThhMDM1NzA3MjgyIiwiYWN0aXZpdGkiOmZhbHNlLCJzY29wZSI6WyJBUFAiXSwiaWQiOjI2MDI2LCJsYW5kbG9yZElkIjoyNjAyNiwiZXhwIjoxNzgyMjgwNTk5LCJqdGkiOiIxZDI2ZDFkNi1hYmQzLTQ0YjUtODg4MS1jOTA2ZTcyZWRlNWQiLCJjbGllbnRfaWQiOiJBUFAifQ.
o72M6ZZLjuse2R6xJ9u7ELUpu-hoDqKpsiqr0RAJiHw
```

| 字段 | 值 | 说明 |
|------|-----|------|
| `id` | 26026 | 用户ID |
| `landlordId` | 26026 | 房东ID（与用户ID相同） |
| `scope` | ["APP"] | 权限范围 |
| `client_id` | "APP" | 客户端标识 |
| `exp` | 1782280599 | 过期时间（2026-02-28） |

### 4.3 Token 传递方式

- **HTTP Header**：`Authorization: Bearer <JWT>`
- **CORS**：`Origin: http://8.153.90.53:8084`

---

## 5. 流式通信分析

**无流式通信检测到**。本次操作采用传统的请求-响应模式（Request-Response），未使用 SSE/WebSocket 等实时推送机制。

---

## 6. 存储使用分析

### 6.1 localStorage 变化

| Key | 值 | 用途 |
|-----|-----|------|
| `tipPop16` | `{"type":"boolean","data":true}` | 弹窗提示标记（避免重复弹窗） |

### 6.2 其他存储引用

前端代码中引用了 `tokenFake` 标记（存储于 Storage），用于判断是否使用模拟 Token。

---

## 7. 关键依赖关系

```
┌─────────────────────────────────────────────────────────┐
│  请求时序与依赖图                                          │
└─────────────────────────────────────────────────────────┘

页面加载 (onLoad)
    │
    ├── 解析 URL 参数 ──────────────────┐
    │                                    │
    ▼                                    │
cotenancyHouseAddEditMore (GET)           │
    │ 获取现有户型数据                    │
    ▼                                    │
用户修改表单 ─────────────────────────────┘
    │
    ├──► wholeHouse/list (POST)  ──► 刷新房源列表
    │
    ▼
cotenancyHouseEdit (POST)  ──► 保存编辑
    │
    ├──► checkHouseIndexPlus (POST) ──► 验证索引
    │
    └──► wholeHouse/list (POST)  ──► 更新显示
```

### 关键依赖

| 依赖关系 | 说明 |
|---------|------|
| URL 参数 → 表单初始化 | `parentId` 用于加载现有户型数据 |
| 表单修改 → 保存提交 | 用户配置决定 `cotenancyHouseEdit` 请求体内容 |
| 保存成功 → 列表刷新 | 保存后重新查询 `wholeHouse/list` 展示最新数据 |

---

## 8. 复现建议

### 8.1 复现代码逻辑

```python
import requests
import json
import time

# 1. 获取有效 Token（需先完成登录）
# Token 应包含: id=26026, scope=["APP"], exp>当前时间

TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

BASE_URL = "http://8.153.90.53:7663"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json; charset=UTF-8",
    "Origin": "http://8.153.90.53:8084",
    "Referer": "http://8.153.90.53:8084/"
}

# 2. 编辑合租户型（核心操作）
edit_payload = {
    "parentId": 1558024,
    "house": [
        {
            "houseId": 0,
            "name": "1室",
            "rent": "333",
            "meterArr": [],
            "doorLockArr": [],
            "waterArr": [],
            "meterAllocationProportion": 1,
            "waterAllocationProportion": 1,
            "houseStatus": {"name": "WAITING_RENT"},
            "isEdit": True,
            "add": True,
            "meterAddForms": [],
            "waterAddForms": []
        },
        {
            "houseId": 0,
            "name": "2室",
            "rent": "444",
            "meterArr": [],
            "doorLockArr": [],
            "waterArr": [],
            "meterAllocationProportion": 1,
            "waterAllocationProportion": 1,
            "houseStatus": {"name": "WAITING_RENT"},
            "isEdit": True,
            "add": True,
            "meterAddForms": [],
            "waterAddForms": []
        }
    ],
    "kitchenNumber": 1,
    "livingRoomNumber": 1,
    "roomNumber": 2,
    "toiletNumber":