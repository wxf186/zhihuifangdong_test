# 协议分析报告

## 1. 场景识别

**操作类型**: 房源添加（合租房源新增）

用户正在通过前端表单提交房源信息，包括地理位置（浙江省杭州市）、小区信息（中天·官河锦庭）、具体房屋信息（11幢11单元1101室）、房屋面积（123㎡）、租金（356元/月）等。

---

## 2. 交互流程概述

```
┌─────────────────────────────────────────────────────────────────────┐
│  时间顺序                                                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  1. [CORS预检]  OPTIONS /core/houseAdd/cotenancyAdd                │
│     ← 200 OK (允许跨域请求)                                        │
│                                                                     │
│  2. [主请求]  POST /core/houseAdd/cotenancyAdd                     │
│     → Body: 房源详细信息 JSON                                      │
│     ← Response: {success:true, data:1558024} (新增房源ID)          │
│                                                                     │
│  3. [列表刷新] POST /core/wholeHouse/list (×2)                     │
│     → 刷新房源列表视图                                             │
│                                                                     │
│  4. [重复提交] POST /core/houseAdd/cotenancyAdd (×1)              │
│     → 再次提交房源数据                                             │
│                                                                     │
│  5. [列表刷新] POST /core/wholeHouse/list (×2)                     │
│     → 刷新房源列表视图                                             │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 3. API端点清单

| 序号 | 方法 | 端点 | 用途 | 鉴权状态 |
|------|------|------|------|----------|
| #42 | OPTIONS | `/core/houseAdd/cotenancyAdd` | CORS预检请求 | 无 |
| #43 | POST | `/core/houseAdd/cotenancyAdd` | 添加合租房源 | Bearer Token |
| - | POST | `/core/wholeHouse/list` | 获取/刷新房源列表 | Bearer Token |

### 关键API详情

#### 3.1 添加合租房源

| 属性 | 值 |
|------|-----|
| **Method** | POST |
| **URL** | `http://8.153.90.53:7663/core/houseAdd/cotenancyAdd` |
| **Content-Type** | `application/json; charset=UTF-8` |
| **请求体** | 见下方 |
| **成功响应** | `{"success":true,"message":"成功","data":1558024}` |

**请求体结构**:
```json
{
  "provinceId": 19,           // 省份ID (浙江省)
  "cityId": 561,              // 城市ID (杭州市)
  "cityName": "杭州市",        // 城市名称
  "communityId": 378773,      // 小区ID
  "communityName": "中天·官河锦庭", // 小区名称
  "block": "11幢",            // 楼栋号
  "unit": "11单元",           // 单元号
  "name": "1101室",           // 房间号
  "area": 123,                // 面积(平方米)
  "rent": 356,                // 月租金(元)
  "cameraVoList": [],         // 摄像头配置(空)
  "newPvCost": true           // 新电费配置标识
}
```

---

## 4. 鉴权机制分析

| 项目 | 分析结果 |
|------|----------|
| **认证方式** | JWT Bearer Token |
| **Token来源** | 请求前通过登录获取，存储于客户端 |
| **传递方式** | HTTP Header: `Authorization: Bearer <token>` |
| **Token结构** | JWT (Header.Payload.Signature) |
| **Payload解码** | `{"password":"5690dddfa28ae085d23518a035707282","active":false,"scope":["APP"],"id":26026,"landlordId":26026,"exp":1782280599,"jti":"1d26d1d6-abd3-44b5-8881-c906e72rede5d","client_id":"APP"}` |

### 鉴权关键字段
- **用户ID**: 26026
- **角色**: 房东 (landlordId: 26026)
- **过期时间**: 1782280599 (Unix时间戳，约2026年)
- **客户端ID**: APP

---

## 5. 流式通信分析

**检测结果**: 无流式通信 (无 SSE/WebSocket)

---

## 6. 存储使用分析

| 存储类型 | Key | 值 | 用途推测 |
|----------|-----|-----|----------|
| localStorage | `tipPop16` | `{"type":"boolean","data":true}` | 弹窗提示标记（避免重复显示某提示） |

---

## 7. 关键依赖关系

```
┌──────────────────────────────────────────────────────────────────┐
│                                                                  │
│  用户登录 ──────────────────────→ 获取 JWT Token                │
│       │                                                           │
│       ▼                                                           │
│  填写房源表单 ────────────────────→ provinceId, cityId, communityId │
│       │                                   block, unit, name       │
│       │                                   area, rent              │
│       ▼                                                           │
│  POST /cotenancyAdd ──────────────→ 创建房源记录                  │
│       │                              返回 houseId (1558024)       │
│       ▼                                                           │
│  POST /wholeHouse/list ───────────→ 刷新房源列表                  │
│       │                              显示新添加的房源             │
│       ▼                                                           │
│  (可能) 编辑设备 ──────────────────→ 关联摄像头/水表/门锁          │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

---

## 8. 复现建议

### 8.1 核心API调用伪代码

```javascript
// ========== 1. 添加合租房源 ==========
const addCotenancyHouse = async () => {
  const response = await fetch(
    'http://8.153.90.53:7663/core/houseAdd/cotenancyAdd',
    {
      method: 'POST',
      headers: {
        'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIs...', // JWT Token
        'Content-Type': 'application/json; charset=UTF-8',
        'Origin': 'http://8.153.90.53:8084',
        'Referer': 'http://8.153.90.53:8084/'
      },
      body: JSON.stringify({
        provinceId: 19,
        cityId: 561,
        cityName: '杭州市',
        communityId: 378773,
        communityName: '中天·官河锦庭',
        block: '11幢',
        unit: '11单元',
        name: '1101室',
        area: 123,
        rent: 356,
        cameraVoList: [],
        newPvCost: true
      })
    }
  );
  
  const result = await response.json();
  // result: { success: true, message: '成功', data: 1558024 }
  // data 字段为新创建的房源ID
  
  return result;
};

// ========== 2. 刷新房源列表 ==========
const refreshHouseList = async () => {
  const response = await fetch(
    'http://8.153.90.53:7663/core/wholeHouse/list',
    {
      method: 'POST',
      headers: {
        'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIs...',
        'Content-Type': 'application/json; charset=utf-8'
      },
      body: JSON.stringify({ /* 分页/筛选参数 */ })
    }
  );
  
  return await response.json();
};
```

### 8.2 完整复现流程

```javascript
// Step 1: 登录获取Token (本数据中Token已存在)
// Token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJwYXNzd29yZCI6...

// Step 2: 调用房源添加API
addCotenancyHouse();

// Step 3: 刷新列表确认添加成功
refreshHouseList();

// Step 4: (可选) 存储弹窗标记
localStorage.setItem('tipPop16', JSON.stringify({
  type: 'boolean',
  data: true
}));
```

---

## 总结

| 分析维度 | 结论 |
|----------|------|
| **业务场景** | 房东添加合租房源信息 |
| **技术架构** | 前端8084端口 → API服务器7663端口 (跨端口通信) |
| **认证机制** | JWT Bearer Token，7天后过期 |
| **通信协议** | HTTP RESTful JSON API |
| **前端框架** | UniApp (基于Vue + 跨平台组件) |
| **关键业务ID** | 小区ID: 378773, 新增房源ID: 1558024, 用户ID: 26026 |