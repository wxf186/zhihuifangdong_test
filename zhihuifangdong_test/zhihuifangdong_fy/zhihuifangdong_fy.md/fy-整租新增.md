# 协议分析报告

## 1. 场景识别

**业务场景：长租公寓/房源管理系统 - 添加整租房源**

用户正在执行房源发布流程，具体操作包括：
- 添加新房源（整租）
- 配置房源户型信息（3室3厅3卫3厨）
- 设置租金和付款方式（月付）
- 配置佣金和押金信息
- 查询房源列表验证添加结果

---

## 2. 交互流程概述

| 顺序 | 操作 | API端点 | 说明 |
|------|------|---------|------|
| 1 | 提交房源信息 | `/core/houseAdd/wholeAdd` | 创建新房源，返回房源ID `1558023` |
| 2 | 查询房源列表 | `/core/wholeHouse/list` | 验证房源添加成功（可能为自动刷新） |
| 3 | 保存佣金配置 | `/findhouse/houseCommissionCofig/save` | 配置房源佣金比例 |
| 4 | 校验房源数据 | `/core/app/house/checkHouseIndexMoreHb` | 校验房源完整性 |

---

## 3. API端点清单

### 3.1 添加房源

| 属性 | 值 |
|------|-----|
| **方法** | `POST` |
| **URL** | `http://8.153.90.53:7663/core/houseAdd/wholeAdd` |
| **用途** | 创建整租房源 |
| **Content-Type** | `application/json; charset=UTF-8` |

**请求体：**
```json
{
  "provinceId": 19,
  "cityId": 561,
  "cityName": "杭州市",
  "communityId": 378773,
  "communityName": "中天·官河锦庭",
  "kitchenNumber": 3,
  "livingRoomNumber": 3,
  "roomNumber": 3,
  "toiletNumber": 3,
  "commission": 50,
  "pledgeCount": 1,
  "perMonth": 1,
  "payMethod": "MONTH_PAY",
  "rent": "650.00",
  "block": "10幢",
  "unit": "10单元",
  "name": "1102室",
  "area": 145,
  "newPvCost": true,
  "houseTitle": "中天·官河锦庭10幢10单元1102室3室3卫-朝南"
}
```

**响应：**
```json
{
  "success": true,
  "message": "成功",
  "data": 1558023
}
```

### 3.2 查询房源列表

| 属性 | 值 |
|------|-----|
| **方法** | `POST` |
| **URL** | `http://8.153.90.53:7663/core/wholeHouse/list` |
| **用途** | 获取房源列表 |

### 3.3 保存佣金配置

| 属性 | 值 |
|------|-----|
| **方法** | `POST` |
| **URL** | `http://8.153.90.53:7663/findhouse/houseCommissionCofig/save` |
| **用途** | 保存房源佣金配置 |
| **Content-Type** | `application/x-www-form-urlencoded;charset=UTF-8` |

### 3.4 校验房源

| 属性 | 值 |
|------|-----|
| **方法** | `POST` |
| **URL** | `http://8.153.90.53:7663/core/app/house/checkHouseIndexMoreHb` |
| **用途** | 校验房源数据完整性 |
| **Content-Type** | `application/x-www-form-urlencoded;charset=UTF-8` |

---

## 4. 鉴权机制分析

### 4.1 认证方式
- **Bearer Token** (JWT)
- 所有请求均携带 `Authorization: Bearer <token>` 请求头

### 4.2 JWT Payload 解码
```json
{
  "password": "5690dddfa28ae085d23518a035707282",
  "active": false,
  "scope": ["APP"],
  "id": 26026,
  "landlordId": 26026,
  "exp": 1782280599,
  "jti": "1d26d1d6-abd3-44b5-8881-c906e72rede5d",
  "client_id": "APP"
}
```

### 4.3 鉴权特征
| 项目 | 值 |
|------|-----|
| **用户ID** | `26026` |
| **房东ID** | `26026` |
| **Token有效期** | 至 `2025-11-21` (时间戳1782280599) |
| **客户端标识** | `APP` |
| **密码哈希** | `5690dddfa28ae085d23518a035707282` (MD5格式) |

---

## 5. 流式通信分析

**无流式通信检测**

本次操作采用传统 HTTP Request/Response 模式，未使用：
- WebSocket
- Server-Sent Events (SSE)
- gRPC Streaming

---

## 6. 存储使用分析

### localStorage 变化
| Key | 类型 | 值 | 用途 |
|-----|------|-----|------|
| `tipPop16` | boolean | `true` | 弹窗提示状态标记（可能表示某提示已显示过） |

### 请求来源分析
- **Origin**: `http://8.153.90.53:8084`
- **Referer**: `http://8.153.90.53:8084/`
- 前端框架：uni-app (基于 Vue)

---

## 7. 关键依赖关系

```
wholeAdd (创建房源)
    ↓ 获取房源ID: 1558023
wholeHouse/list (查询列表验证)
    ↓
houseCommissionCofig/save (配置佣金)
    ↓
checkHouseIndexMoreHb (数据校验)
```

**前置条件**：需要有效的 JWT Token (Bearer)

---

## 8. 复现建议

### Python 伪代码实现

```python
import requests
import json

BASE_URL = "http://8.153.90.53:7663"

# Step 1: 准备认证Token
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json; charset=UTF-8",
    "Origin": "http://8.153.90.53:8084",
    "Referer": "http://8.153.90.53:8084/"
}

# Step 2: 添加整租房源
house_data = {
    "provinceId": 19,
    "cityId": 561,
    "cityName": "杭州市",
    "communityId": 378773,
    "communityName": "中天·官河锦庭",
    "kitchenNumber": 3,
    "livingRoomNumber": 3,
    "roomNumber": 3,
    "toiletNumber": 3,
    "commission": 50,
    "pledgeCount": 1,
    "perMonth": 1,
    "payMethod": "MONTH_PAY",
    "rent": "650.00",
    "block": "10幢",
    "unit": "10单元",
    "name": "1102室",
    "area": 145,
    "newPvCost": True,
    "houseTitle": "中天·官河锦庭10幢10单元1102室3室3卫-朝南"
}

response = requests.post(
    f"{BASE_URL}/core/houseAdd/wholeAdd",
    headers=HEADERS,
    json=house_data
)
house_id = response.json()["data"]

# Step 3: 查询房源列表验证
requests.post(
    f"{BASE_URL}/core/wholeHouse/list",
    headers=HEADERS,
    json={}
)

# Step 4: 保存佣金配置
requests.post(
    f"{BASE_URL}/findhouse/houseCommissionCofig/save",
    headers={
        **HEADERS,
        "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8"
    },
    data=f"houseId={house_id}&commission=50"
)

# Step 5: 校验房源
requests.post(
    f"{BASE_URL}/core/app/house/checkHouseIndexMoreHb",
    headers={
        **HEADERS,
        "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8"
    },
    data=f"houseId={house_id}"
)
```

---

## 9. 附加分析：前端页面特征

从 JS 代码片段分析 `addRoomHe` 组件：

| 功能 | 实现 |
|------|------|
| 户型选择