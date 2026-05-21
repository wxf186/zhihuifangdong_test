

# 协议分析报告

## 1. 场景识别

**场景类型**：房东社区列表查询（房源管理后台操作）

**操作判断**：用户通过移动端（Android 13，微信内核）访问"智慧房东"类应用，携带 JWT Bearer Token 和 Session Cookie 查询特定城市（上海-奉贤区）的房东社区列表数据。

**关键特征**：
- 域名 `api.zhihuifangdong.net` → 智慧房东平台
- 接口 `houseManageExt/showLandLordCommunity` → 社区管理功能
- 查询参数包含 `cityName=奉贤区`、`provinceId=1`、`provinceName=上海市`
- 返回 `records: []` 空数据集

---

## 2. 交互流程概述

| 顺序 | 步骤 | 说明 |
|------|------|------|
| 1 | **会话建立** | 多次 GET `/s/CQfbH90lNjAaZqXX4OyrfA` 建立 Session（Set-Cookie） |
| 2 | **身份鉴权** | POST `/rest/aaid/get` 获取设备认证并更新 Cookie |
| 3 | **业务查询** | 携带 Bearer Token + Cookie 查询房东社区列表 |
| 4 | **结果返回** | 获取空数据集（无社区记录） |

---

## 3. API 端点清单

| 方法 | 端点 | 用途 | 鉴权方式 |
|------|------|------|----------|
| GET | `/s/{sessionId}` | 建立会话，获取 Session Cookie | 无 |
| POST | `/rest/aaid/get` | 设备认证，获取/刷新 Cookie | 请求体含设备信息 |
| GET | `/core/app/houseManageExt/showLandLordCommunity` | 查询房东社区列表 | Bearer Token + Cookie |

### 核心业务接口详情

```
GET https://api.zhihuifangdong.net/core/app/houseManageExt/showLandLordCommunity
```

**Query 参数**：
| 参数 | 值 | 含义 |
|------|-----|------|
| current | 1 | 当前页 |
| size | 10000 | 每页数量（极大值，可能为全量查询） |
| cityName | 奉贤区 | 城市名称 |
| provinceId | 1 | 省份ID |
| provinceName | 上海市 | 省份名称 |

**响应结构**：
```json
{
  "success": true,
  "message": "成功",
  "data": {
    "total": 0,       // 无数据
    "size": 10000,
    "pages": 0,
    "current": 1,
    "records": []     // 空数组
  }
}
```

---

## 4. 鉴权机制分析

### 认证架构

```
┌──────────────┐     ┌──────────────────┐     ┌─────────────────────────┐
│   移动端     │────▶│  Session Cookie  │────▶│  Bearer JWT Token        │
│  (Android)   │     │  (会话级)        │     │  (应用级)                │
└──────────────┘     └──────────────────┘     └─────────────────────────┘
```

### JWT Token 解码

**Authorization Header**：
```
Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJwYXNzd29yZCI6IjU2OTBkZGRmYTI4YWUwODVkMjM1MThhMDM1NzA3MjgyIiwiYWN0aXZpdGkiOmZhbHNlLCJzY29wZSI6WyJhcHAiXSwiaWQiOjE4MTQxMTQsImxhbmRsb3JkSWQiOjE4MTQxMTQsImV4cCI6MTc4MDcyMzkzNiwianRpIjoiNDdjYzkwMmUtOTcyNC00ZmFmLWIxMGYtYzc4MDc3MDM0ZGE1IiwiY2xpZW50X2lkIjoiQVBQIn0.rPhYFawgYjb5zUEqtNkxv6K1I8Lkxo_h_oWHsDYhiq8
```

**Payload 解析**：
| 字段 | 值 | 含义 |
|------|-----|------|
| id | 1814114 | 用户ID |
| landlordId | 1814114 | 房东ID |
| scope | ["app"] | 权限范围：仅App |
| exp | 1780723936 | 过期时间（2026-06-03） |
| jti | 47c9902e-9724-4faf-b10f-c78077034da5 | JWT ID |

**特征分析**：
- 使用 `HS256` 算法签名
- `password` 字段存在于 Payload 中（**安全风险**）
- 包含 `landlordId` 字段，标识房东身份
- `client_id` 为 `APP`，表示移动应用客户端

---

## 5. 流式通信分析

**检测结果**：无流式通信

未检测到 SSE、WebSocket 或其他流式传输协议。所有请求均为标准 HTTP Request/Response 模式。

---

## 6. 存储使用分析

### Cookie 使用

| Cookie 名称 | 来源 | 用途 |
|-------------|------|------|
| acw_tc | `/core/app/*` 响应 | 访问控制/防CSRF |
| Session Cookie | `/s/CQfbH90lNjAaZqXX4OyrfA` | 会话标识 |

**关键 Cookie 样本**：
```
acw_tc=0a24eec517784837145206056e019e6ec61791b563bbb1a2186360a2c48fae
```

### localStorage/sessionStorage

**分析结果**：未检测到相关变更

---

## 7. 关键依赖关系

```
时间线
─────────────────────────────────────────────────────────────▶
     │              │              │              │
     ▼              ▼              ▼              ▼
┌─────────┐  ┌─────────┐  ┌─────────┐  ┌────────────────────────┐
│GET /s/* │  │GET /s/* │  │GET /s/* │  │POST /rest/aaid/get     │
│建立会话  │  │保持会话  │  │验证会话  │  │设备认证(更新Cookie)    │
└────┬────┘  └────┬────┘  └────┬────┘  └───────────┬────────────┘
     │            │            │                    │
     └────────────┴────────────┴────────────────────┘
                            │
                            ▼
              ┌─────────────────────────────┐
              │GET /core/app/* (最终请求)   │
              │携带: Authorization + Cookie │
              │返回: 业务数据               │
              └─────────────────────────────┘
```

**依赖关系说明**：
1. 必须先完成 Session 建立（获取 Cookie）
2. 可选进行设备认证（刷新 Cookie）
3. 最终业务请求需同时携带 Session Cookie + Bearer Token

---

## 8. 复现建议

### 伪代码实现

```python
import requests
import json
import jwt

# ========== 1. 会话建立 ==========
session = requests.Session()

# 获取 Session Cookie
session.get("https://api.zhihuifangdong.net/s/CQfbH90lNjAaZqXX4OyrfA")

# ========== 2. 设备认证（可选） ==========
# session.post(
#     "https://api.zhihuifangdong.net/rest/aaid/get",
#     json={"deviceId": "xxx", "deviceInfo": "xxx"}
# )

# ========== 3. 构造 Bearer Token ==========
# 注意：此处需要从客户端获取实际 Token
token_payload = {
    "password": "5690dddfa28ae085d23518a035707282",
    "active": False,
    "scope": ["app"],
    "id": 1814114,
    "landlordId": 1814114,
    "exp": 1780723936,
    "jti": "47c9902e-9724-4faf-b10f-c78077034da5",
    "client_id": "APP"
}
# JWT Header: {"alg":"HS256","typ":"JWT"}
token = jwt.encode(token_payload, "签名密钥", algorithm="HS256")

# ========== 4. 业务查询 ==========
headers = {
    "authorization": f"Bearer {token}",
    "content-type": "application/x-www-form-urlencoded;charset=UTF-8",
    "user-agent": "Mozilla/5.0 (Linux; Android 13; ...) Chrome/101.0.4951.74 Mobile Safari/537.36"
}

params = {
    "current": 1,
    "size": 10000,
    "cityName": "奉贤区",
    "provinceId": 1,
    "provinceName": "上海市"
}

response = session.get(
    "https://api.zhihuifangdong.net/core/app/houseManageExt/showLandLordCommunity",
    headers=headers,
    params=params
)

print(response.json())
```

### 复现注意事项

| 要素 | 说明 |
|------|------|
| **JWT 签名** | 需要服务器的 HS256 签名密钥 |
| **Token 有效期** | 截至 2026-06-03，需在有效期内使用 |
| **Cookie 传递** | 需保持 Session Cookie 与 Token 匹配 |
| **User-Agent** | 移动端标识，建议使用 Android 设备 UA |
| **地区查询** | 奉贤区 + 上海，切换地区需修改参数 |

---

## 附录：技术栈推断

| 组件 | 推断技术 |
|------|----------|
| 前端框架 | 微信小程序/H5（基于 User-Agent 中的 Immersed 字段） |
| 后端架构 | Java 微服务（基于 `/rest/` 路径风格） |
| 数据库 | IndexedDB（用于本地缓存，由 Dexie.js 管理） |
| 认证方案 | JWT + Session Cookie

---

## Follow-up Chat

**User**:

列出该接口的api参数和响应结构

**AI**:

## 接口 API 参数与响应结构

### 请求信息

| 属性 | 值 |
|------|-----|
| **URL** | `https://api.zhihuifangdong.net/core/app/houseManageExt/accurateSearch` |
| **方法** | POST |
| **Content-Type** | `application/x-www-form-urlencoded` |

---

### 请求参数（Form Data）

| 参数名 | 示例值 | 类型 | 含义 |
|--------|--------|------|------|
| `rentType` | `COTENANCY` | String | 租赁类型（合租模式） |
| `keyWord` | `东` | String | 搜索关键词（UTF-8 URL编码） |

---

### 响应结构

```json
{
  "success": true,          // boolean  请求是否成功
  "message": "成功",        // string   响应消息
  "data": {                 // object   业务数据
    "communityList": [],    // array    社区/小区列表
    "houseList": [],        // array    房源列表
    "userList": [],         // array    用户列表
    "snList": [],           // array    序列号列表
    "remarkList": []        // array    备注列表
  }
}
```

---

### data.communityList 数组结构（当有数据时）

| 字段 | 类型 | 示例值 | 含义 |
|------|------|--------|------|
| `communityId` | Number | `144934` | 小区ID |
| `communityName` | String | `"东和雅苑"` | 小区名称 |
| `districtName` | String | `"鄞州区"` | 所属区域 |
| `labels` | Number | `0` | 标签标识 |

**响应示例（含数据）**：
```json
{
  "success": true,
  "message": "成功",
  "data": {
    "communityList": [
      {
        "communityId": 144934,
        "communityName": "东和雅苑",
        "districtName": "鄞州区",
        "labels": 0
      },
      {
        "communityId": 395875,
        "communityName": "合嵣悦府东区",
        "districtName": "余杭区",
        "labels": 0
      }
    ],
    "houseList": [],
    "userList": [],
    "snList": [],
    "remarkList": []
  }
}
```

---

### 通用响应字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `success` | Boolean | `true`=成功，`false`=失败 |
| `message` | String | 中文描述信息 |
| `data` | Object | 业务数据载体，结构因接口而异 |

> **注**：该接口为精准搜索/自动补全类接口，当 `keyWord` 为空时返回空数组 `[]`。其他列表接口（如 `cotenancyHouse/list`）采用分页结构 `current/size/pages/records`。
