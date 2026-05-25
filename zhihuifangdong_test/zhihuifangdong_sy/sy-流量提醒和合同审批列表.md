
# 协议分析报告：智慧水务应用 - 设备状态监控场景

## 1. 场景识别

**业务场景**：智慧水务/物联网设备管理系统 - **水表流量监控与预警**

**核心行为**：
- 高频轮询水表逾期流量提醒状态
- 查询合同审批列表（无数据状态）
- 持续后台监控模式（非交互式操作）

---

## 2. 交互流程概述

```
┌─────────────────────────────────────────────────────────────────────┐
│                        时间线与操作序列                               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  [会话初始化]                                                        │
│      │                                                              │
│      ▼                                                              │
│  #7 GET fluxRemindWindow  ──→  data: false (无流量提醒窗口)          │
│      │                                                              │
│      ▼                                                              │
│  #9 GET fluxRemindWindowOverdue ──→  data: true (存在逾期提醒)        │
│      │                                                              │
│      ▼                                                              │
│  #18 POST contractApproval/list ──→  data: [] (无待审批合同)          │
│      │                                                              │
│      ▼                                                              │
│  [轮询阶段 - 约25次重复请求]                                          │
│      │                                                              │
│      ▼                                                              │
│  #101-#677 GET fluxRemindWindowOverdue (间隔: 约5-20秒)               │
│      │                                                              │
│      ▼                                                              │
│  #677-678 POST contractApproval/list (重试查询)                      │
│      │                                                              │
│      ▼                                                              │
│  #679-#749 GET fluxRemindWindowOverdue (继续轮询)                     │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 3. API 端点清单

| 编号 | 方法 | 端点路径 | 用途 | 请求参数 | 响应格式 |
|:----:|:----:|----------|------|----------|----------|
| #7 | GET | `/netty/web/meter/fluxRemindWindow` | 流量提醒窗口检测 | `userId=1814114` | `{"success":true,"data":false}` |
| #9, #101-#749 | GET | `/netty/web/meter/fluxRemindWindowOverdue` | 逾期流量提醒状态轮询 | `userId=1814114` | `{"success":true,"data":boolean}` |
| #18, #677-678 | POST | `/core/contractApproval/list` | 合同审批列表查询 | JSON: `{"approvalStatus":"INIT","current":1,"size":N}` | `{"success":true,"data":{"total":0,"records":[]}}` |

### API 特征分析

```javascript
// 轮询端点特征
Endpoint: https://api.zhihuifangdong.net/netty/web/meter/fluxRemindWindowOverdue
Method: GET
Content-Type: application/x-www-form-urlencoded;charset=UTF-8
轮询间隔: 约5-20秒（不规则）
重复次数: 约25次
响应特征: 仅返回布尔值

// 查询端点特征
Endpoint: https://api.zhihuifangdong.net/core/contractApproval/list
Method: POST
Content-Type: application/json; charset=utf-8
Body: {"approvalStatus":"INIT","current":1,"size":9999|10}
响应特征: 分页数据结构
```

---

## 4. 鉴权机制分析

### 4.1 认证方式

```
┌────────────────────────────────────────────────────┐
│                   JWT Bearer Token                   │
├────────────────────────────────────────────────────┤
│  算法: HS256 (HMAC with SHA-256)                   │
│  格式: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.*      │
└────────────────────────────────────────────────────┘
```

### 4.2 Token Payload 解析

```json
{
  "password": "5690dddfa28ae085d23518a035707282",
  "active": false,
  "scope": ["app"],
  "id": 1814114,
  "landlordId": 1814114,
  "exp": 1780723936,
  "jti": "47cc902e-9724-4faf-b10f-c78077034da5",
  "client_id": "APP"
}
```

### 4.3 鉴权信息汇总

| 项目 | 值 |
|------|-----|
| 用户ID | `1814114` |
| 客户端ID | `APP` |
| 作用域 | `app` |
| Token类型 | Bearer |
| 过期时间 | 2026-12-04 (Unix: 1780723936) |
| 认证头格式 | `Authorization: Bearer <token>` |

### 4.4 Cookie 使用

```
Cookie: acw_tc=0a24eec217781316188253097e70d27baf7fa35e65ba805ecba8da29c51a13
用途: 阿里云安全防护验证 (AntCloud Web Application Firewall)
```

---

## 5. 流式通信分析

**检测结果**：无流式通信

所有请求均为传统 HTTP Request/Response 模式，无 SSE/WebSocket/WebRTC 等流式协议。

---

## 6. 存储使用分析

| 存储类型 | 键名 | 值 | 变化 |
|----------|------|-----|------|
| Cookie | `acw_tc` | `0a24eec217781316188253097e70d27baf7fa35e65ba805ecba8da29c51a13` | 无变化（静态传递） |
| localStorage | - | - | 无记录 |
| sessionStorage | - | - | 无记录 |

**结论**：本场景未涉及前端存储操作，所有数据通过请求头传递。

---

## 7. 关键依赖关系

```
fluxRemindWindow (首次检测)
       │
       ├── false → 继续轮询 fluxRemindWindowOverdue
       │
       └── (异步触发) → 后续业务逻辑

fluxRemindWindowOverdue (高频轮询)
       │
       ├── true → 可能触发 UI 提醒或消息推送
       │
       └── (循环) → 持续监控直到状态变更

contractApproval/list (条件触发)
       │
       ├── size=9999 → 初始化全量查询
       │
       └── size=10 → 分页重试查询
```

### 轮询时间间隔分析

```
请求间隔估算（基于编号差异）:
- #9 → #101: 约 10-20 秒
- #101 → #136: 约 5-10 秒
- #677 → #679: 约 1-2 秒（快速连续）
- #679 → #749: 约 10-20 秒
```

---

## 8. 复现建议

### 8.1 Python 伪代码实现

```python
import requests
import time
import json

class SmartWaterMonitor:
    """智慧水务 - 水表流量监控复现类"""
    
    BASE_URL = "https://api.zhihuifangdong.net"
    USER_ID = "1814114"
    
    def __init__(self, token: str):
        self.session = requests.Session()
        self.token = token
        self.session.headers.update({
            "Authorization": f"Bearer {token}",
            "User-Agent": "Mozilla/5.0 (Linux; Android 13; V2219A Build/TP1A.220624.014; wv)...",
            "Cookie": "acw_tc=0a24eec217781316188253097e70d27baf7fa35e65ba805ecba8da29c51a13"
        })
    
    def check_flux_remind_window(self) -> bool:
        """检查流量提醒窗口状态"""
        url = f"{self.BASE_URL}/netty/web/meter/fluxRemindWindow"
        params = {"userId": self.USER_ID}
        response = self.session.get(url, params=params)
        data = response.json()
        return data.get("data", False)
    
    def check_flux_remind_overdue(self) -> bool:
        """检查逾期流量提醒状态（轮询核心）"""
        url = f"{self.BASE_URL}/netty/web/meter/fluxRemindWindowOverdue"
        params = {"userId": self.USER_ID}
        response = self.session.get(url, params=params)
        data = response.json()
        return data.get("data", False)
    
    def query_contract_approval_list(self, size: int = 10) -> dict:
        """查询合同审批列表"""
        url = f"{self.BASE_URL}/core/contractApproval/list"
        body = {
            "approvalStatus": "INIT",
            "current": 1,
            "size": size
        }
        response = self.session.post(url, json=body)
        return response.json()
    
    def start_monitoring(self, interval: float = 10.0, duration: int = 3600):
        """启动监控流程"""
        print(f"[监控启动] 用户ID: {self.USER_ID}")
        
        # 1. 初始检测
        has_window = self.check_flux_remind_window()
        print(f"[初始检测] 流量提醒窗口: {has