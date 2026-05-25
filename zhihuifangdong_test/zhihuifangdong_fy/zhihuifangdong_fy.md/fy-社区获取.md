# 协议分析报告

## 1. 场景识别

**用户操作类型：** 小区搜索与选择（房产/租房场景）

用户通过输入小区名称关键词（如"信息"、"信"、"新"）进行小区检索操作，选择城市ID=6758（上海市奉贤区）进行搜索。

---

## 2. 交互流程概述

```
┌─────────────────────────────────────────────────────────────┐
│                    小区搜索流程                               │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. [认证准备] ← 获取 Session Cookie (多次 Set-Cookie)       │
│         ↓                                                     │
│  2. [认证] ← Bearer Token 鉴权 (JWT)                         │
│         ↓                                                     │
│  3. [搜索1] GET /core/app/house/getCommunity?name=信息       │
│         ↓                                                     │
│  4. [搜索2] GET /core/app/house/getCommunity?name=信         │
│         ↓                                                     │
│  5. [搜索3] GET /core/app/house/getCommunity?name=新         │
│         ↓                                                     │
│  6. [结果展示] 返回小区列表数据 (含ID、名称、区域信息)         │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

**详细流程：**

1. **认证阶段**：通过多次 GET 请求获取 Session Cookie，后续通过 JWT Bearer Token 完成身份认证
2. **搜索阶段**：用户逐步输入更简短的关键词进行模糊搜索
   - 输入"信息"→ 无结果
   - 输入"信"→ 无结果
   - 输入"新"→ 返回11条小区数据

---

## 3. API端点清单

| 序号 | 方法 | 路径 | 用途 | 鉴权方式 |
|:----:|:----:|------|------|:--------:|
| #262 | GET | `/core/app/house/getCommunity` | 小区名称搜索（关键词："信息"） | Bearer Token |
| #263 | GET | `/core/app/house/getCommunity` | 小区名称搜索（关键词："信"） | Bearer Token |
| #264 | GET | `/core/app/house/getCommunity` | 小区名称搜索（关键词："新"） | Bearer Token |

### API 请求参数分析

| 参数 | 类型 | 示例值 | 说明 |
|------|:----:|--------|------|
| `name` | String | `新` | 小区名称搜索关键词（URL编码） |
| `cityId` | Integer | `6758` | 城市ID（6758 = 上海市） |

### API 响应格式

```json
{
  "success": true,
  "message": "成功",
  "data": {
    "小区ID": {
      "小区名称": "区域-街道-详细地址"
    }
  }
}
```

---

## 4. 鉴权机制分析

### 认证方式
- **主认证**：Bearer Token (JWT) 
- **辅助认证**：Session Cookie

### JWT Token 解析

```javascript
// Header
{
  "alg": "HS256",
  "typ": "JWT"
}

// Payload
{
  "password": "5690dddfa28ae085d23518a035707282",
  "active": false,
  "scope": ["app"],
  "id": 1814114,
  "landlordId": 1814114,
  "exp": 1780723936,        // 2026年6月3日过期
  "jti": "47cc902e-9724-4faf-b10f-c78077034da5",
  "client_id": "APP"
}
```

### 凭据传递方式

| 传递方式 | 位置 | 内容 |
|---------|------|------|
| Authorization Header | `Bearer eyJhbGci...` | JWT Token |
| Cookie | `acw_tc=0a24eec5...` | 风险控制Token |
| 路径参数 | `/s/CQfbH90lNjAaZqXX4OyrfA` | Session ID |

### 鉴权链时序

```
Session Cookie 获取:
GET /s/CQfbH90lNjAaZqXX4OyrfA → Set-Cookie (重复3次)
POST /rest/aaid/get → Set-Cookie (1次)

↓
    
Bearer Token 使用:
GET /core/app/house/getCommunity 
  → Authorization: Bearer <JWT>
  → Cookie: acw_tc=...
```

---

## 5. 流式通信分析

**检测结果：** 无流式通信

本次交互中所有请求均为标准 HTTP 短连接，未检测到：
- Server-Sent Events (SSE)
- WebSocket
- HTTP/2 Server Push

所有响应均为同步 JSON 格式。

---

## 6. 存储使用分析

### Cookie 使用情况

| Cookie Key | 用途 | 可见性 | 过期策略 |
|------------|------|:------:|----------|
| `acw_tc` | 阿里云风险控制标识 | 客户端可见 | Session |

```javascript
// Cookie 设置示例
acw_tc=0a24eec517784837145206056e019e6ec61791b563bbb1a2186360a2c48fae
```

### Storage 使用情况

| 存储类型 | 使用情况 |
|----------|:--------:|
| localStorage | 未使用 |
| sessionStorage | 未使用 |
| IndexedDB | 未使用（存在相关代码但未触发） |

---

## 7. 关键依赖关系

### 请求时序图

```
时间线 ──────────────────────────────────────────────────→

认证准备 ────────────→ 搜索#262 ──→ 搜索#263 ──→ 搜索#264
     ↓                    ↓           ↓            ↓
  [Session]          [name=信息]  [name=信]    [name=新]
  [Cookie]           [data={}]   [data={}]   [data={...}]
                       (空结果)    (空结果)     (11条数据)
```

### 依赖关系说明

| 依赖类型 | 说明 |
|----------|------|
| **认证依赖** | 所有搜索请求均依赖有效的 JWT Token，Token 过期时间约至 2026年 |
| **业务逻辑依赖** | 搜索请求之间无依赖关系，可并行执行 |
| **Cookie 依赖** | `acw_tc` Cookie 需随请求携带 |

---

## 8. 复现建议

### 完整复现逻辑（伪代码）

```python
import requests
import json

class HouseSearchClient:
    def __init__(self):
        self.session = requests.Session()
        self.base_url = "https://api.zhihuifangdong.net"
        self.jwt_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
        
    def get_session_cookie(self):
        """步骤1: 获取 Session Cookie"""
        urls = [
            f"{self.base_url}/s/CQfbH90lNjAaZqXX4OyrfA",
            f"{self.base_url}/rest/aaid/get"
        ]
        for url in urls:
            self.session.get(url)
        return self.session.cookies.get_dict()
    
    def search_community(self, name: str, city_id: int = 6758) -> dict:
        """步骤2: 搜索小区"""
        url = f"{self.base_url}/core/app/house/getCommunity"
        headers = {
            "Authorization": f"Bearer {self.jwt_token}",
            "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
            "User-Agent": "Mozilla/5.0 (Linux; Android 13; ...) Chrome/101.0.4951.74"
        }
        params = {"name": name, "cityId": city_id}
        
        response = self.session.get(url, headers=headers, params=params)
        return response.json()
    
    def execute_search_flow(self):
        """执行完整搜索流程"""
        # 1. 初始化认证
        self.get_session_cookie()
        
        # 2. 逐个搜索关键词
        keywords = ["信息", "信", "新"]
        results = {}
        
        for keyword in keywords:
            result = self.search_community(keyword)
            results[keyword] = result
            print(f"搜索 '{keyword}': {len(result.get('data', {}))} 条结果")
            
        return results

# 执行复现
client = HouseSearchClient()
client.execute_search_flow()
```

### 关键参数提取

```python
# 核心参数
SEARCH_PARAMS = {
    "name": "新",              # 搜索关键词
    "cityId": 6758             # 上海市
}

# JWT Payload
JWT_PAYLOAD = {
    "id": 1814114,             # 用户ID
    "landlordId": 1814114,     # 房东ID
    "client_id": "APP",        # 客户端类型
    "scope": ["app"]           # 权限范围
}

# 响应数据示例
RESPONSE_EXAMPLE = {
    "success": True,
    "message": "成功",
    "data": {
        "281642": {
            "新南家园": "-西渡-西闸公路1118弄"
        }
    }
}
```

---

## 9. 技术特征总结

| 特征项 | 描述 |
|--------|------|
| **应用类型** | 移动端房产/租房应用 |
| **API 架构** | RESTful JSON API |
| **认证机制** | JWT Bearer Token + Session Cookie |
| **加密情况** | 存在 crypto.subtle SHA-512 代码但未使用 |
| **数据格式** | JSON (URL-encoded params) |
| **城市ID映射** | 6758 → 上海市 |

---

**报告生成时间：** 协议分析完成  
**数据来源：** Zhihuifangdong.net 应用流量