

# 协议分析报告：房源佣金配置保存

## 1. 场景识别

**业务场景**：房源佣金配置管理
**具体操作**：用户为指定房源（ID: 2749273）设置租金及佣金分成规则并保存

**关键特征**：
- 认证方式：Bearer JWT Token + Session Cookie 双轨制
- 业务类型：HTTP 表单提交（application/x-www-form-urlencoded）
- 响应类型：JSON API 同步返回

---

## 2. 交互流程概述

```
[认证初始化]
GET /s/CQfbH90lNjAaZqXX4OyrfA
  └─→ Set-Cookie: acw_tc (多次重复，可能为重试/刷新机制)

[身份验证]
POST /rest/aaid/get  
  └─→ Set-Cookie: 更新会话状态

[业务操作]
POST /findhouse/houseCommissionCofig/save
  ├─ Header: Authorization: Bearer <JWT>
  ├─ Cookie: acw_tc
  └─ Body: houseId=2749273&houseRent=320.00&configs=[...]
      └─→ Response: {"success":true,"message":"保存成功"}
```

---

## 3. API 端点清单

| # | 方法 | 端点 | 用途 | 认证方式 |
|---|------|------|------|----------|
| 1 | GET | `/s/CQfbH90lNjAaZqXX4OyrfA` | 会话初始化/保持 | None |
| 2 | POST | `/rest/aaid/get` | 获取认证凭证 | Session Cookie |
| 3 | POST | `/findhouse/houseCommissionCofig/save` | 保存佣金配置 | Bearer Token |

### 核心业务 API 详情

```
POST https://api.zhihuifangdong.net/findhouse/houseCommissionCofig/save

Headers:
  authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
  content-type: application/x-www-form-urlencoded;charset=UTF-8
  cookie: acw_tc=0a24eec517784837145206056e019e6ec61791b563bbb1a2186360a2c48fae
  user-agent: Mozilla/5.0 (Linux; Android 13; V2219A Build/TP1A.220624.014; wv)...

Request Body:
  houseId=2749273
  houseRent=320.00
  configs=[{"commissionType":2,"commissionValue":50,"startMonth":1,"endMonth":null}]

Response:
  {"success":true,"message":"保存成功"}
```

---

## 4. 鉴权机制分析

### 认证方式：JWT Bearer Token

**JWT Token 结构**：
```javascript
{
  "password": "5690dddfa28ae085d23518a035707282",  // 密码哈希 (MD5)
  "activity": false,
  "scope": ["app"],
  "id": 1814114,           // 用户ID
  "ladm_id": 1814114,      // 登录管理员ID
  "exp": 1780723936,       // 过期时间戳 (2026-06-02)
  "jti": "47cc902e-9724-4faf-b10f-c78077034da5",  // JWT ID
  "client_id": "APP"       // 客户端标识
}
```

**Token 获取流程**：
1. 获取 Session Cookie → 保持会话状态
2. 调用 `POST /rest/aaid/get` → 触发认证，生成/刷新 JWT
3. 业务请求携带 Bearer Token

**凭据传递**：
- Cookie `acw_tc`：用于安全追踪/反爬机制
- Authorization Header：JWT Bearer Token

---

## 5. 存储使用分析

| 存储类型 | 键名 | 来源 | 用途 |
|---------|------|------|------|
| Cookie | `acw_tc` | `GET /s/...` Set-Cookie | 安全追踪 |
| Cookie | `acw_tc` | `POST /rest/aaid/get` Set-Cookie | 更新会话 |

**注意**：未检测到 localStorage/sessionStorage 使用，业务数据完全通过 API 传输。

---

## 6. 关键依赖关系

```
时间线依赖：
                    GET /s/CQfbH90lNjAaZqXX4OyrfA
                              ↓
                    POST /rest/aaid/get
                              ↓
                    POST /save (业务操作)

Token 依赖：
  JWT Token 有效期 → 影响业务请求成功率
  需要 Token 包含正确 ladm_id=1814114
```

---

## 7. 复现建议

```javascript
// 复现流程伪代码

// Step 1: 初始化会话
fetch('GET /s/CQfbH90lNjAaZqXX4OyrfA', {
  credentials: 'include'
});
// 捕获 Set-Cookie: acw_tc=...

// Step 2: 获取认证 Token
const response = await fetch('POST /rest/aaid/get', {
  method: 'POST',
  credentials: 'include'
});
// 捕获 JWT Token (Authorization: Bearer ...)

// Step 3: 保存佣金配置
await fetch('POST /findhouse/houseCommissionCofig/save', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer eyJhbGci...',
    'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8'
  },
  body: new URLSearchParams({
    houseId: '2749273',
    houseRent: '320.00',
    configs: JSON.stringify([{
      commissionType: 2,
      commissionValue: 50,
      startMonth: 1,
      endMonth: null
    }])
  }),
  credentials: 'include'
});

// 预期响应: {"success":true,"message":"保存成功"}
```

---

## 8. 补充说明

- **无流式通信**：所有请求均为同步 HTTP，无 SSE/WebSocket
- **无加密操作**：业务数据以明文表单形式传输，JWT 自带签名验证
- **设备信息**：User-Agent 显示为 Android 13 移动设备（vivo V2219A）
- **关联代码**：Dexie 库（IndexedDB 封装）出现在 JS 中，但未执行本地存储操作