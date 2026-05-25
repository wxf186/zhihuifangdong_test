

# 协议分析报告：智慧房设备价格查询

## 1. 场景识别

**操作类型**：智能家居/物业管理系统中的 **设备价格查询**

用户正在访问"智慧方"（zhihuifangdong.net）物业平台，查询特定小区的设备（水表、电表等）计费配置信息。

---

## 2. 交互流程概述

```
┌─────────────────────────────────────────────────────────────────────┐
│                         用户会话初始化流程                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  [客户端]                              [服务器]                        │
│     │                                     │                          │
│     ├─── GET /s/CQfbH90lNjAaZqXX4OyrfA ──►│  (获取Session Cookie)    │
│     │◄── Set-Cookie: SESSION_ID ◄─────────│                         │
│     │                                     │                          │
│     ├─── GET /s/CQfbH90lNjAaZqXX4OyrfA ──►│  (再次获取Session)       │
│     │◄── Set-Cookie: (重复) ◄─────────────│                         │
│     │                                     │                          │
│     ├─── POST /rest/aaid/get ────────────►│  (AAID鉴权)              │
│     │◄── Set-Cookie: (再次确认) ◄─────────│                          │
│     │                                     │                          │
│     └─── GET /core/manual/selectDevice    │                          │
│            PriceHandle?communityId=...───►│  (查询设备价格)          │
│     │◄── JSON Response ◄─────────────────│                          │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 3. API 端点清单

| # | 方法 | 路径 | 用途 |
|---|------|------|------|
| 1 | GET | `/s/{sessionToken}` | Session Cookie 获取（未知端点） |
| 2 | POST | `/rest/aaid/get` | AAID 认证接口 |
| 3 | GET | `/core/manual/selectDevicePriceHandle` | **核心**：查询设备价格配置 |

### 核心 API 详情

```
GET https://api.zhihuifangdong.net/core/manual/selectDevicePriceHandle

Query Parameters:
├── communityId = 362440    (小区ID)
└── type = 1                (设备类型标识)

Request Headers:
├── authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
├── content-type: application/x-www-form-urlencoded;charset=UTF-8
├── user-agent: Mozilla/5.0 (Linux; Android 13; V2219A...)
└── cookie: acw_tc=0a24eec51778...

Response Body:
{
  "success": true,
  "message": "成功",
  "data": {
    "id": 11037,
    "all": true,
    "meterPrice": "1.000",         ← 电费单价
    "userId": 1814114,
    "createTime": "2025-03-31 19:22:35",
    "updateTime": "2025-06-10 09:11:01",
    "rentType": "WHOLE",           ← 整租模式
    "meter": true,                 ← 有电表
    "coldWater": true,             ← 有冷水表
    "water": false,                ← 无热水
    "coal": false,                 ← 无暖气
    "meterPriceType": false,
    "ladderPrice": [               ← 阶梯电价配置
      {"level":"1","price":"1","start":"","end":"10"},
      {"level":"2","price":"1.1","start":"10","end":"100"},
      {"level":"3","price":"1.2","start":"100"}
    ]
  }
}
```

---

## 4. 鉴权机制分析

### 认证方式
- **Primary**: JWT Bearer Token（`Authorization: Bearer <token>`）
- **Secondary**: Session Cookie + AAID

### JWT Token 结构解析

```javascript
Header: { "alg": "HS256", "typ": "JWT" }
Payload: {
  "password": "5690dddfa28ae085d23518a035707282",  // ⚠️ 密码哈希值泄露
  "active": false,
  "scope": ["app"],
  "id": 1814114,           // 用户ID
  "landlordId": 1814114,    // 房东ID
  "exp": 1780723936,        // 2026-03-14 过期
  "jti": "47cc902e-9724-4faf-b10f-c78077034da5",
  "client_id": "APP"
}
Signature: rPhYFawgYjb5zUEqtNkxv6K1I8Lkxo_h_oWHsDYhiq8
```

### 鉴权链传递
```
1. /s/{token}          → Set-Cookie (SESSION)
2. /rest/aaid/get      → Set-Cookie (SESSION)  
3. /core/manual/...    → Cookie: acw_tc=... + Authorization: Bearer JWT
```

---

## 5. 存储使用分析

| 存储类型 | Key | 值 | 用途 |
|---------|-----|---|------|
| Cookie | `acw_tc` | `0a24eec517784837145206056e019e6ec61791b563bbb1a2186360a2c48fae` | 访问跟踪 |
| Cookie | `SESSION` | (来自 /s/ 端点) | 会话维持 |

---

## 6. 加密代码分析

### 检测到的加密操作

```javascript
// 来源: wx.qq.com CDN 资源 (非业务代码)
// 位置: indexdb.moy1e6kg8d829639.js (Dexie.js 库)

if ("undefined" == typeof crypto || !crypto.subtle)
    return [e, s(e), e];

var t = crypto.subtle.digest("SHA-512", new Uint8Array([0]));
```

**说明**：这是 Dexie.js（IndexedDB 封装库）内部的 SHA-512 哈希，用于其 Promise 实现的安全检查，**与业务鉴权无关**。

---

## 7. 关键依赖关系

```
┌─────────────────────────────────────────────────────────────┐
│                        时序依赖图                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  /s/{token} (GET)                                          │
│       │                                                    │
│       ▼  Set-Cookie                                        │
│  POST /rest/aaid/get                                       │
│       │                                                    │
│       ▼  Set-Cookie                                        │
│  GET /core/manual/selectDevicePriceHandle                   │
│       │                                                    │
│       ▼  Response (设备价格JSON)                            │
│                                                             │
└─────────────────────────────────────────────────────────────┘

依赖关系：
1. /s/ 和 /rest/aaid/get 为前置准备（获取/刷新 Session）
2. 最终设备查询需依赖 Bearer Token 的有效性
```

---

## 8. 复现建议

```python
import requests
import json

# 1. 会话初始化（获取 Cookie）
session = requests.Session()

# Step 1: 获取 Session Cookie
session.get(
    "https://api.zhihuifangdong.net/s/CQfbH90lNjAaZqXX4OyrfA",
    headers={"User-Agent": "..."}
)

# Step 2: AAID 认证
session.post(
    "https://api.zhihuifangdong.net/rest/aaid/get",
    headers={"Content-Type": "application/x-www-form-urlencoded"}
)

# 3. 查询设备价格
response = session.get(
    "https://api.zhihuifangdong.net/core/manual/selectDevicePriceHandle",
    params={"communityId": 362440, "type": 1},
    headers={
        "Authorization": "Bearer eyJhbGci...",
        "User-Agent": "Mozilla/5.0 (Linux; Android 13; V2219A..."
    }
)

data = response.json()
print(f"电费单价: {data['data']['meterPrice']} 元/度")
print(f"阶梯电价: {data['data']['ladderPrice']}")
```

---

## 9. 敏感信息发现

| 类型 | 风险等级 | 描述 |
|------|---------|------|
| 🔴 密码哈希暴露 | **高** | JWT payload 中包含 `password` 字段（哈希值） |
| 🟡 Token 长期有效 | **中** | exp 时间戳显示 2026-03-14 过期 |
| 🟡 弱签名算法 | **中** | 使用 HS256 而非 RS256 |

---

**分析完成时间**：2025-06-10  
**数据覆盖范围**：部分会话（缺少完整的登录流程记录）