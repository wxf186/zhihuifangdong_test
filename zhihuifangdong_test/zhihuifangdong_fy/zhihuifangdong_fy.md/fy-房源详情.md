

# 协议分析报告：智慧房管查询操作

## 一、场景识别

**用户操作类型**：房源详情查询（房屋信息查询）

用户通过移动端 App（Android）查询指定房源编号（`id=2749274`）的详细信息，包括房源状态（未出租）、面积、租金、户型配置、小区信息等。

---

## 二、交互流程概述

按时间顺序排列：

| 阶段 | 步骤 | 操作 |
|------|------|------|
| **① 初始化** | #246（最早） | 携带预置 Authorization Bearer Token 向 `api.zhihuifangdong.net` 发起 `POST /core/checkHouseIndexPlus` 请求 |
| **② 页面导航** | Cookie 注入 | 访问 `GET /s/CQfbH90lNjAaZqXX4OyrfA`，服务端通过 `Set-Cookie` 设置会话 Cookie |
| **③ 再次访问** | Cookie 刷新 | 重复访问 `GET /s/CQfbH90lNjAaZqXX4OyrfA`，再次 `Set-Cookie` |
| **④ 三次访问** | Cookie 再次刷新 | 第三次访问 `GET /s/CQfbH90lNjAaZqXX4OyrfA`，再次 `Set-Cookie` |
| **⑤ AAID 注册** | 广告标识符上报 | `POST /rest/aaid/get` → `Set-Cookie` 保存 AAID |

> 核心业务请求是 **步骤①** 的 `checkHouseIndexPlus` 查询，其余均为辅助性请求（页面初始化、Cookie 维护、广告标识上报）。

---

## 三、API 端点清单

| # | 方法 | 路径 | 用途 | 关键参数 |
|---|------|------|------|---------|
| 1 | `POST` | `/core/checkHouseIndexPlus` | **查询房源详情** | `id=2749274`（房源 ID） |
| 2 | `GET` | `/s/CQfbH90lNjAaZqXX4OyrfA` | 页面初始化/会话建立 | — |
| 3 | `POST` | `/rest/aaid/get` | 广告标识符（AAID）上报 | — |

### 核心业务接口详细分析

**POST /core/checkHouseIndexPlus**

```
请求地址：https://api.zhihuifangdong.net/core/checkHouseIndexPlus
请求方法：POST
Content-Type：application/x-www-form-urlencoded;charset=UTF-8
鉴权方式：Authorization: Bearer <JWT>
请求体：id=2749274
```

**响应数据结构：**

```json
{
  "success": true,
  "message": "成功",
  "data": {
    "id": 2749274,
    "name": "9幢1单元101室",          // 房源名称
    "communityName": "合嵣悦府东区",   // 小区名称
    "communityId": 395875,            // 小区 ID
    "districtName": "余杭区",          // 行政区
    "area": 87.0,                      // 面积（㎡）
    "rent": "301.00",                  // 月租金（元）
    "houseStatus": {
      "message": "未出租",
      "name": "WAITING_RENT"           // 状态枚举
    },
    "roomNumber": 2,                   // 卧室数
    "kitchenNumber": 1,                // 厨房数
    "toiletNumber": 1,                 // 卫生间数
    "livingRoomNumber": 1,             // 客厅数
    "houseFeatures": "",               // 房屋特征标签
    "elevator": true,                  // 有无电梯
    "sonHouse": [...]                  // 分房间源列表
  }
}
```

---

## 四、鉴权机制分析

### 4.1 认证方式

**JWT Bearer Token**，通过 HTTP 头部 `Authorization` 字段传递：

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJwYXNzd29yZCI6IjU2OTBkZGRmYTI4YWUwODVkMjM1MThhMDM1NzA3MjgyIiwiYWN0aXZpdGkiOmZhbHNlLCJzY29wZSI6WyJhcHAiXSwiaWQiOjE4MTQxMTQsImxhbmRsb3JkSWQiOjE4MTQxMTQsImV4cCI6MTc4MDcyMzkzNiwianRpIjoiNDdjYzkwMmUtOTcyNC00ZmFmLWIxMGYtYzc4MDc3MDM0ZGE1IiwiY2xpZW50X2lkIjoiQVBQIn0.rPhYFawgYjb5zUEqtNkxv6K1I8Lkxo_h_oWHsDYhiq8
```

### 4.2 JWT Payload 解码

```json
{
  "password": "5690dddfa28ae085d23518a035707282",  // 密码 MD5 哈希值
  "active": false,
  "scope": ["app"],
  "id": 1814114,                                    // 用户 ID
  "landlordId": 1814114,                            // 房东 ID（同用户 ID）
  "exp": 1780723936,                                // 有效期截止时间戳
  "jti": "47cc902e-9724-4faf-b10f-c78077034da5",   // JWT 唯一标识
  "client_id": "APP"                               // 客户端类型
}
```

### 4.3 凭据获取流程

```
┌─────────────────────────────────────────────────────────────┐
│                    隐式 Token 预分发                         │
│  (Token 由服务端预先生成并嵌入客户端，客户端携带此 Token 请求)  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
                 POST /core/checkHouseIndexPlus
                 Authorization: Bearer <Token>
                              │
                              ▼
                       服务端验证 JWT
                       (exp, password hash, client_id)
```

### 4.4 凭据传递方式

| 凭据类型 | 传递方式 | Header/Cookie |
|---------|---------|--------------|
| **JWT Bearer Token** | Authorization Header | `Authorization: Bearer eyJ...` |
| **acw_tc 设备标识** | Cookie | `cookie: acw_tc=0a24eec5...` |
| **Session Cookie** | Set-Cookie 响应 | 服务端逐次 Set-Cookie |

### 4.5 会话 Cookie 维护链

```
GET /s/CQfbH90lNjAaZqXX4OyrfA  → Set-Cookie (Session)
GET /s/CQfbH90lNjAaZqXX4OyrfA  → Set-Cookie (Session)  ← 重复刷新
GET /s/CQfbH90lNjAaZqXX4OyrfA  → Set-Cookie (Session)  ← 重复刷新
POST /rest/aaid/get             → Set-Cookie (AAID)
```

---

## 五、流式通信分析

**无流式通信（SSE/WebSocket）**

未检测到 Server-Sent Events 或 WebSocket 握手。核心接口采用 **同步 REST** 模式（请求-响应）。

---

## 六、存储使用分析

| 存储类型 | 键名 | 来源 | 用途 |
|---------|------|------|------|
| **Cookie** | `acw_tc` | 固定值 | 设备/客户端标识 |
| **Cookie** | Session Cookie | `GET /s/...` 响应 Set-Cookie | 会话维持 |
| **Cookie** | — | `POST /rest/aaid/get` 响应 Set-Cookie | AAID（广告标识符） |

> 本次操作记录中未检测到 `localStorage` / `sessionStorage` 的写入变化。

---

## 七、关键依赖关系

```
┌──────────────────────┐
│  Session Cookie 获取  │  ← GET /s/CQfbH90lNjAaZqXX4OyrfA
└──────────┬───────────┘
           │
           ▼ (可选，Cookie 注入后才发起)
┌──────────────────────┐
│ AAID Cookie 获取      │  ← POST /rest/aaid/get
└──────────┬───────────┘
           │
           ▼
┌──────────────────────────────────────────────────────┐
│  核心业务请求：checkHouseIndexPlus                    │
│  (依赖 Authorization Bearer Token + acw_tc Cookie)  │
└──────────────────────────────────────────────────────┘
           │
           ▼
    返回房源详情 JSON
```

### 时序关系

1. **Session Cookie** 为可选前置步骤（可能由 WebView 自动加载页面触发