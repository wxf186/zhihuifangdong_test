

# 智慧房管平台 HTTP 协议分析报告

## 1. 场景识别

**场景类型：房屋租赁管理平台 - 房源查询与筛选操作**

| 维度 | 判定 |
|------|------|
| 操作类型 | 查询类（Read-Only） |
| 业务领域 | 智慧房管/长租公寓管理 |
| 用户角色 | 运营/管理人员 |
| 使用设备 | Android 手机（Android 13, V2219A） |
| 目标城市 | 杭州市 |

**核心操作描述：** 用户通过移动端对多个小区（合嵣悦府东区、新安新秀家园北二区、海创绿谷等）的合租房源进行多维度状态查询和筛选。

---

## 2. 交互流程概述

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          完整交互链路                                     │
└─────────────────────────────────────────────────────────────────────────┘

时间顺序：

[阶段1: 鉴权初始化]
 GET /s/CQfbH90lNjAaZqXX4OyrfA          → 获取 Session Cookie
 GET /s/CQfbH90lNjAaZqXX4OyrfA          → 刷新 Session Cookie
 GET /s/CQfbH90lNjAaZqXX4OyrfA          → 刷新 Session Cookie
 POST /rest/aaid/get                     → 获取设备鉴权令牌

[阶段2: 房源查询 - 小区A]
 #2 POST /core/cotenancyHouse/list      → 查询"合嵣悦府东区"全部房源

[阶段3: 房源查询 - 小区B筛选]
 #4 POST /core/cotenancyHouse/list      → 查询"新安新秀家园北二区"(带关键词"东")
 #6 POST /core/cotenancyHouse/list      → 筛选"等待出租"状态(带关键词)
 #7 POST /core/cotenancyHouse/list      → 筛选"等待出租"状态(不带关键词) → 返回3条
 #8 POST /core/cotenancyHouse/list      → 筛选"已出租"状态 → 0条
 #9 POST /core/cotenancyHouse/list      → 筛选"出租签订中" → 返回1条
 #10 POST /core/cotenancyHouse/list     → 筛选"已入住"状态 → 0条
 #11 POST /core/cotenancyHouse/list      → 筛选"未出租"状态 → 0条
 #12-20                                → 多维度组合筛选(朝向+房间号+状态)
 #21-24                                → 排序参数测试(sort, usort, vacantDay)
 #232                                  → 再次请求"等待出租"状态

[阶段4: 全量查询 - 脱离小区上下文]
 #235 POST /core/cotenancyHouse/list     → 全量查询"等待出租"房源 → 返回39条
 #244-272                              → 多次全量查询 → 返回41条(数据更新)
```

---

## 3. API 端点清单

### 3.1 鉴权相关

| # | 方法 | 路径 | 用途 | 响应特征 |
|---|------|------|------|----------|
| - | GET | `/s/{sessionId}` | Session Cookie 获取 | Set-Cookie |
| - | POST | `/rest/aaid/get` | 设备认证 | Set-Cookie |

### 3.2 业务核心

| # | 方法 | 路径 | 用途 | 请求数 |
|---|------|------|------|--------|
| #2 | POST | `/core/cotenancyHouse/list` | 合租房源列表查询(小区维度) | 1 |
| #4-232 | POST | `/core/cotenancyHouse/list` | 合租房源筛选查询 | 21 |
| #235-272 | POST | `/core/cotenancyHouse/list` | 全量房源查询 | 38 |

---

### 3.3 请求体结构分析

```json
// 基础结构
{
  "current": 1,                    // 当前页码
  "size": 12,                      // 每页条数(默认12)
  "orientations": [],              // 朝向筛选: ["朝南","朝西","朝北",...]
  "roomNumbers": [],               // 房间号筛选: [1,2,3,4]
  "houseStatus": "WAITING_RENT",   // 房屋状态筛选
  "cityName": "杭州市",            // 城市
  "communityId": 188660,           // 小区ID
  "communityName": "新安新秀家园北二区", // 小区名称
  "keywords": "东",                // 关键词搜索
  "sort": false,                   // 排序开关
  "usort": false,                 // 用户排序
  "vacantDay": false              // 空置天数筛选
}
```

### 3.4 houseStatus 枚举值

| 值 | 含义 | 响应数据量 |
|----|------|-----------|
| `WAITING_RENT` | 未出租/等待出租 | 3条(小区) / 41条(全量) |
| `RENTED` | 已出租 | 0条 |
| `LEASE_SIGNING` | 出租签订中 | 1条 |
| `PRE_LINE` | 已入住/入住中 | 0条 |
| `NOT_RENT` | 未出租 | 0条 |

---

## 4. 鉴权机制分析

### 4.1 认证方式

```
┌─────────────────────────────────────────────────────────────────┐
│                         双重鉴权机制                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  [Layer 1] Session Cookie                                        │
│  ├── 来源: GET /s/CQfbH90lNjAaZqXX4OyrfA (多次)                 │
│  ├── Cookie名: acw_tc                                           │
│  └── 用途: 设备追踪/CSRF防护                                     │
│                                                                  │
│  [Layer 2] JWT Bearer Token                                      │
│  ├── 来源: Authorization Header                                 │
│  ├── 格式: Bearer eyJhbGciOiJIUzI1NiIs...                       │
│  └── Payload关键字段:                                            │
│       { "id": 1814114,          // 用户ID                         │
│         "password": "5690dd...", // 密码Hash                      │
│         "active": false,        // 激活状态                       │
│         "scope": ["app"],       // 授权范围                       │
│         "exp": 1780723936,      // 过期时间(2026-06)              │
│         "client_id": "APP" }   // 客户端标识                     │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 4.2 Token 传递方式

```
请求头:
  Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
  Cookie: acw_tc=0a24eec517784837145206056e019e6ec61791b563bbb1a2186360a2c48fae
```

### 4.3 JWT 解码后的关键信息

| 字段 | 值 | 说明 |
|------|-----|------|
| `id` | 1814114 | 用户唯一标识 |
| `landlordId` | 1814114 | 房东/管理员ID (与用户ID相同) |
| `exp` | 1780723936 | 2026年6月过期 |
| `client_id` | APP | 应用类型标识 |
| `scope` | ["app"] | 权限范围 |

---

## 5. 流式通信分析

**结论：未检测到流式通信(SSE/WebSocket)**

- 所有请求均为标准 Request-Response 模式
- 响应均为 JSON 结构体
- 无 Server-Sent Events 或 WebSocket 升级
- 页面刷新机制: 每次请求完整页面数据

---

## 6. 存储使用分析

### 6.1 Cookie 使用

| Cookie名 | 值(哈希) | 来源 | 用途推测 |
|----------|----------|------|----------|
| `acw_tc` | `0a24eec517784837145206056e019e6ec61791b563bbb1a2186360a2c48fae` | 所有请求自动携带 | 防CSRF / 设备指纹 / 行为追踪 |

### 6.2 IndexedDB 使用

从加密代码片段分析，系统使用了 **Dexie.js** (IndexedDB 封装库):

```javascript
// 关键代码特征
crypto.subtle.digest("SHA-512", ...)  // 哈希计算
Dexie.Promise                          // IndexedDB 异步操作
location.href.test(/localhost|127\.0\.0\.1/)  // 本地调试检测
```

**推测用途：**
- 本地缓存房源数据
- 离线数据暂存
- 用户行为日志本地存储

---

## 7. 关键依赖关系

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           请求依赖时序图                                  │
└─────────────────────────────────────────────────────────────────────────┘

[无依赖] 所有 /core/cotenancyHouse/list 请求互为独立
        └── 均携带相同的 Authorization Token
        └── 均携带相同的 Cookie
        └── 无前置请求依赖

[数据关联]
  #235 全量查询(39条)
       ↓ 数据更新
  #244 全量查询(41条)  ← 数据量变化(+2条)

[参数变化规律]
  请求间主要差异在于 houseStatus 枚举值切换
  城市固定为"杭州市"
  小区ID在 188660 / 192039