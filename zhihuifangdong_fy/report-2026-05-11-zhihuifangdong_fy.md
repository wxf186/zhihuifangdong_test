

# 协议分析报告：智慧房东 App 房源管理操作

## 1. 场景识别

**场景类型**：房源管理 - 新增整租/合租房源、配置佣金

用户通过智慧房东 App 执行了以下核心操作：
- 小区搜索与浏览
- 新增整租房源（整租）
- 新增合租房源（合租）
- 合租房分间编辑
- 房源佣金配置

---

## 2. 交互流程概述

| 顺序 | 操作阶段 | 关键行为 |
|------|----------|----------|
| 1 | 初始化认证 | 携带 JWT Bearer Token 发起所有请求 |
| 2 | 小区搜索 | 通过关键词"东"搜索匹配小区 |
| 3 | 合租房浏览 | 遍历多个小区的合租房状态（待租/出租中/未租） |
| 4 | 查看房源详情 | 获取房源索引信息 |
| 5 | 新增整租房源 | 填写房源信息并提交 |
| 6 | 新增合租房源 | 创建合租单元并添加子房间 |
| 7 | 配置佣金 | 设置佣金比例（50%） |
| 8 | 切换城市（上海） | 尝试添加上海房源 |
| 9 | 批量添加公寓 | 批量创建公寓房型 |

---

## 3. API 端点清单

### 3.1 房源搜索

| 方法 | 路径 | 用途 |
|------|------|------|
| POST | `/core/app/houseManageExt/accurateSearch` | 精确搜索小区，返回匹配小区列表 |

### 3.2 合租房管理

| 方法 | 路径 | 用途 |
|------|------|------|
| POST | `/core/cotenancyHouse/list` | 合租房列表查询，支持多维度筛选（状态、户型、租金等） |
| GET | `/core/wholeHouse/getBlock` | 获取合租房栋座信息 |

### 3.3 房源详情

| 方法 | 路径 | 用途 |
|------|------|------|
| GET | `/core/app/house/getHouseIndex` | 获取房源索引详情（整租） |
| GET | `/core/app/house/getCotenancyHouseIndex` | 获取合租房详情 |
| POST | `/core/checkHouseIndexPlus` | 校验房源完整性 |

### 3.4 房源新增

| 方法 | 路径 | 用途 |
|------|------|------|
| POST | `/core/houseAdd/wholeAdd` | 新增整租房源 |
| POST | `/core/houseAdd/cotenancyAdd` | 新增合租房源单元 |
| POST | `/core/houseAdd/cotenancyHouseEdit` | 合租房分间编辑（新增/修改子房间） |

### 3.5 地区选择

| 方法 | 路径 | 用途 |
|------|------|------|
| GET | `/core/app/house/provinceChoose` | 获取省份列表 |
| GET | `/core/app/house/cityChooseA?id={provinceId}` | 根据省份 ID 获取城市列表 |
| GET | `/core/app/house/getCommunity` | 搜索小区 |

### 3.6 佣金配置

| 方法 | 路径 | 用途 |
|------|------|------|
| POST | `/findhouse/houseCommissionConfig/save` | 保存房源佣金配置 |

### 3.7 批量公寓

| 方法 | 路径 | 用途 |
|------|------|------|
| GET | `/core/web/template/choose` | 获取公寓模版列表 |
| POST | `/core/web/apartment/addMore` | 批量添加公寓 |

### 3.8 设备价格

| 方法 | 路径 | 用途 |
|------|------|------|
| GET | `/core/manual/selectDevicePriceHandle` | 获取设备计价配置（水电煤等） |

---

## 4. 鉴权机制分析

### 4.1 认证方式

```
JWT Bearer Token (Authorization Header)
```

### 4.2 Token Payload 结构

```json
{
  "password": "5690dddfa28ae085d23518a035707282",
  "activity": false,
  "scope": ["app"],
  "id": 1814114,
  "landmarkId": 1814114,
  "exp": 1780723936,
  "jti": "47cc902e-9724-4faf-b10f-c78077034da5",
  "client_id": "APP"
}
```

### 4.3 Token 传递方式

| 场景 | 传递方式 |
|------|----------|
| 请求头 | `Authorization: Bearer <token>` |
| Cookie | `acw_tc` 用于防 CSRF 校验 |

### 4.4 凭据生命周期

- **Token 有效期**：exp=1780723936 (约 2026-05-22)
- **用户 ID**：1814114

---

## 5. 关键依赖关系

```
时间线 → API 调用链

[1] 初始搜索 → accurateSearch(keyWord="东")
         ↓
[2] 选择小区 → cotenancyHouse/list(communityId=395875)
         ↓
[3] 获取栋座 → getBlock(type=COTENANCY)
         ↓
[4] 切换小区 → cotenancyHouse/list(communityId=188660)
         ↓
[5-13] 状态筛选 → WAITING_RENT/RENTED/LEASE_SIGNING/NOT_RENT
         ↓
[226] 查看房源 → getHouseIndex
         ↓
[227-229] 选择省市 → provinceChoose → cityChooseA(id=19)
         ↓
[231] 新增整房 → wholeAdd (ID: 2749273)
         ↓
[233-234] 校验+配置佣金 → checkHouseIndexMoreHb → houseCommissionConfig/save
         ↓
[236-243] 新增合房 → cotenancyAdd → cotenancyHouseEdit (ID: 2749274)
         ↓
[246] 校验合房 → checkHouseIndexPlus
         ↓
[251-257] 切换上海 → provinceChoose → cityChooseA(id=1)
         ↓
[270] 批量添加 → addMore (公寓)
```

---

## 6. 数据结构示例

### 6.1 整租房新增请求

```json
{
  "provinceId": 19,
  "cityId": 561,
  "cityName": "杭州市",
  "communityId": 362440,
  "communityName": "中天·官河锦庭",
  "block": "9幢",
  "unit": "1单元",
  "name": "102室",
  "area": 87,
  "rent": "320.00",
  "roomNumber": 2,
  "livingRoomNumber": 1,
  "kitchenNumber": 1,
  "toiletNumber": 1,
  "payMethod": "SEASON_PAY",
  "pledgeCount": 1,
  "perMonth": 3,
  "commission": 50,
  "newPvCost": true
}
```

### 6.2 合租房分间编辑请求

```json
{
  "parentId": 2749274,
  "house": [
    {"houseId": 0, "name": "1011", "rent": "300", "houseStatus": {"name": "WAITING_RENT"}},
    {"houseId": 0, "name": "1012", "rent": "400", "houseStatus": {"name": "WAITING_RENT"}}
  ],
  "payMethod": "MONTH_PAY",
  "pledgeCount": 1,
  "perMonth": 1,
  "roomNumber": 2,
  "livingRoomNumber": 1,
  "kitchenNumber": 1,
  "toiletNumber": 1
}
```

---

## 7. 复现建议

### 7.1 整体复现逻辑

```python
# 1. 认证准备
token = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
headers = {
    "Authorization": token,
    "Content-Type": "application/json"
}

# 2. 新增整租房
whole_add_resp = requests.post(
    "https://api.zhihuifangdong.net/core/houseAdd/wholeAdd",
    headers=headers,
    json={
        "provinceId": 19, "cityId": 561,
        "communityId": 362440, "block": "9幢",
        "unit": "1单元", "name": "102室",
        "area": 87, "rent": "320.00",
        "roomNumber": 2, "payMethod": "SEASON_PAY"
    }
)
house_id = whole_add_resp.json()["data"]  # 2749273

#

---

## Follow-up Chat

**User**:

列出所有 API 参数和响应结构

**AI**:

---

# 智慧房东 App API 参数与响应结构完整文档

## 1. 小区精确搜索

### POST `/core/app/houseManageExt/accurateSearch`

**请求头**：
```
Authorization: Bearer <jwt_token>
Content-Type: application/x-www-form-urlencoded
Cookie: acw_tc=<csrf_token>
```

**请求参数** (form-data)：

| 参数名 | 类型 | 必填 | 说明 | 示例值 |
|--------|------|------|------|--------|
| rentType | String | 是 | 租赁类型 | `COTENANCY`(合租) / `WHOLE`(整租) |
| keyWord | String | 是 | 搜索关键词 | `东` |

**响应结构** (JSON)：

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

## 2. 合租房列表查询

### POST `/core/cotenancyHouse/list`

**请求头**：
```
Authorization: Bearer <jwt_token>
Content-Type: application/json; charset=utf-8
```

**请求参数** (JSON body)：

| 参数名 | 类型 | 必填 | 说明 | 示例值 |
|--------|------|------|------|--------|
| current | Integer | 是 | 当前页码 | `1` |
| size | Integer | 是 | 每页数量 | `12` |
| orientations | Array | 否 | 朝向筛选 | `[]` |
| roomNumbers | Array | 否 | 户型筛选 | `[]` |
| communityId | Long | 否 | 小区ID | `395875` |
| keywords | String | 否 | 关键词 | `东` |
| cityName | String | 否 | 城市名 | `杭州市` |
| communityName | String | 否 | 小区名 | `新安新秀家园北二区` |
| houseStatus | String | 否 | 房源状态 | `WAITING_RENT` |
| sort | Boolean | 否 | 排序 | `true` / `false` |
| usort | Boolean | 否 | 反向排序 | `false` |
| vacantDay | Boolean | 否 | 空置天数筛选 | `false` |

**房源状态枚举**：

| 枚举值 | 含义 |
|--------|------|
| `WAITING_RENT` | 未出租 |
| `RENTED` | 已出租 |
| `LEASE_SIGNING` | 出租签订中 |
| `NOT_RENT` | 未租出 |

**响应结构** (JSON)：

```json
{
  "success": true,
  "message": "成功",
  "data": {
    "total": 39,
    "size": 12,
    "pages": 4,
    "current": 1,
    "records": [
      {
        "communityId": 395875,
        "communityName": "合嵣悦府东区",
        "cityName": "杭州市",
        "simpleHouseList": [
          {
            "id": 2670363,
            "name": "9幢1单元02室",
            "current": 1,
            "sonHouse": [
              {
                "id": 2670364,
                "name": "01",
                "houseStatus": {
                  "message": "出租签订中",
                  "name": "LEASE_SIGNING"
                },
                "rent": 1800.00,
                "rentType": "COTENANCY",
                "dayNumber": 45,
                "current": 1,
                "index": 0,
                "meter": false,
                "water": false,
                "door": false,
                "camera": false
              }
            ]
          }
        ],
        "houseNumTotal": 3,
        "c": "..."
      }
    ],
    "meterUesdAnalyzeMap": {},
    "meterUesdNumAnalyzeMap": {},
    "meterUesdAnalyzeExportMap": {},
    "meterUesdNumAnalyzeExportMap": {},
    "meterTimeRangeMap": {}
  }
}
```

---

## 3. 合租栋座获取

### GET `/core/wholeHouse/getBlock`

**请求头**：
```
Authorization: Bearer <jwt_token>
Content-Type: application/x-www-form-urlencoded;charset=UTF-8
```

**请求参数** (Query)：

| 参数名 | 类型 | 必填 | 说明 | 示例值 |
|--------|------|------|------|--------|
| type | String | 是 | 房源类型 | `COTENANCY` |

**响应结构** (JSON)：

```json
{
  "success": true,
  "message": "成功",
  "data": [
    {
      "cityName": "全部",
      "list": [
        {
          "communityName": "杜诗苑二期",
          "communityId": 393500,
          "housedent": [
            {
              "blocked": "5幢",
              "dent": [
                {
                  "united": "1单元",
                  "floos": [3, 6]
                }
              ]
            }
          ]
        }
      ]
    }
  ]
}
```

---

## 4. 新增整租房源

### POST `/core/houseAdd/wholeAdd`

**请求头**：
```
Authorization: Bearer <jwt_token>
Content-Type: application/json; charset=utf-8
```

**请求参数** (JSON body)：

| 参数名 | 类型 | 必填 | 说明 | 示例值 |
|--------|------|------|------|--------|
| provinceId | Integer | 是 | 省份ID | `19` |
| cityId | Integer | 是 | 城市ID | `561` |
| cityName | String | 是 | 城市名 | `杭州市` |
| communityId | Long | 是 | 小区ID | `362440` |
| communityName | String | 是 | 小区名 | `中天·官河锦庭` |
| block | String | 是 | 楼幢 | `9幢` |
| unit | String | 是 | 单元 | `1单元` |
| name | String | 是 | 房号 | `102室` |
| area | Double | 是 | 面积(㎡) | `87` |
| rent | String | 是 | 月租金(元) | `320.00` |
| roomNumber | Integer | 是 | 卧室数量 | `2` |
| livingRoomNumber | Integer | 是 | 客厅数量 | `1` |
| kitchenNumber | Integer | 是 | 厨房数量 | `1` |
| toiletNumber | Integer | 是 | 卫生间数量 | `1` |
| payMethod | String | 是 | 付款方式 | `SEASON_PAY` |
| pledgeCount | Integer | 是 | 押金月数 | `1` |
| perMonth | Integer | 是 | 付几月 | `3` |
| commission | Integer | 是 | 佣金比例(%) | `50` |
| newPvCost | Boolean | 是 | 是否新计费方式 | `true` |
| houseTitle | String | 否 | 房源标题 | `中天·官河锦庭9幢1单元102室2室1卫-朝南` |

**付款方式枚举**：

| 枚举值 | 含义 |
|--------|------|
| `MONTH_PAY` | 月付 |
| `SEASON_PAY` | 季付 |
| `HALF_YEAR_PAY` | 半年付 |
| `YEAR_PAY` | 年付 |

**响应结构** (JSON)：

```json
{
  "success": true,
  "message": "成功",
  "data": 2749273  // 新增房源ID
}
```

---

## 5. 新增合租房源

### POST `/core/houseAdd/cotenancyAdd`

**请求头**：
```
Authorization: Bearer <jwt_token>
Content-Type: application/json; charset=utf-8
```

**请求参数** (JSON body)：

| 参数名 | 类型 | 必填 | 说明 | 示例值 |
|--------|------|------|------|--------|
| provinceId | Integer | 是 | 省份ID | `19` |
| cityId | Integer | 是 | 城市ID | `561` |
| cityName | String | 是 | 城市名 | `杭州市` |
| communityId | Long | 是 | 小区ID | `395875` |
| communityName | String | 是 | 小区名 | `合嵣悦府东区` |
| block | String | 是 | 楼幢 | `9幢` |
| unit | String | 是 | 单元 | `1单元` |
| name | String | 是 | 房号 | `101室` |
| area | Double | 是 | 面积(㎡) | `87` |
| rent | Double | 是 | 月租金(元) | `301` |
| cameraVoList | Array | 否 | 摄像头配置 | `[]` |
| newPvCost | Boolean | 是 | 是否新计费方式 | `true` |

**响应结构** (JSON)：

```json
{
  "success": true,
  "message": "成功",
  "data": 2749274  // 新复合租房ID(parentId)
}
```

---

## 6. 合租房分间编辑

### POST `/core/houseAdd/cotenancyHouseEdit`

**请求头**：
```
Authorization: Bearer <jwt_token>
Content-Type: application/json; charset=utf-8
```

**请求参数** (JSON body)：

| 参数名 | 类型 | 必填 | 说明 | 示例值 |
|--------|------|------|------|--------|
| parentId | Long | 是 | 合租房父ID | `2749274` |
| house | Array | 是 | 房间列表 | `[...]` |
| kitchenNumber | Integer | 是 | 厨房数量 | `1` |
| livingRoomNumber | Integer | 是 | 客厅数量 | `1` |
| roomNumber | Integer | 是 | 卧室数量 | `2` |
| toiletNumber | Integer | 是 | 卫生间数量 | `1` |
| payMethod | String | 是 | 付款方式 | `MONTH_PAY` |
| pledgeCount | Integer | 是 | 押金月数 | `1` |
| perMonth | Integer | 是 | 付几月 | `1` |

**house 数组元素结构**：

| 参数名 | 类型 | 说明 | 示例值 |
|--------|------|------|--------|
| houseId | Long | 房间ID(新增为0) | `0` |
| name | String | 房间名 | `1011` |
| rent | String | 月租金 | `300` |
| houseStatus.name | String | 房间状态 | `WAITING_RENT` |
| isEdit | Boolean | 是否编辑 | `true` |
| add | Boolean | 是否新增 | `true` |
| meterArr | Array | 电表配置 | `[]` |
| doorLockArr | Array | 门锁配置 | `[]` |
| waterArr | Array | 水表配置 | `[]` |
| meterAllocationProportion | Double | 电费分摊比例 | `1` |
| waterAllocationProportion | Double | 水费分摊比例 | `1` |
| meterAddForms | Array | 电表添加表单 | `[]` |
| waterAddForms | Array | 水表添加表单 | `[]` |

**响应结构** (JSON)：

```json
{
  "success": true,
  "message": "成功"
}
```

---

## 7. 房源详情查询

### GET `/core/app/house

**User**:

缺少批量公寓接口参数和响应结构

**AI**:

---

# 补充：批量公寓接口参数与响应结构

## 8. 公寓模版选择

### GET `/core/web/template/choose`

**请求头**：
```
Authorization: Bearer <jwt_token>
Content-Type: application/x-www-form-urlencoded;charset=UTF-8
```

**请求参数**：无（GET请求无需参数）

**响应结构** (JSON)：

```json
{
  "success": true,
  "message": "成功",
  "data": [
    {
      "id": 5844,
      "name": "独栋模版1",
      "area": 101.0,
      "rent": "300",
      "roomDetail": "3室1厅1厨1卫"
    },
    {
      "id": 8500,
      "name": "新模板",
      "area": 123.0,
      "rent": "308",
      "roomDetail": "2室1厅1厨1卫"
    },
    {
      "id": 8501,
      "name": "zzz",
      "area": 123.0,
      "rent": "111",
      "roomDetail": "3室2厅2厨1卫"
    },
    {
      "id": 8584,
      "name": "佣金30模版",
      "area": 56.0,
      "rent": "560",
      "roomDetail": "2室1厅1厨1卫"
    }
  ]
}
```

**模版字段说明**：

| 字段名 | 类型 | 说明 | 示例值 |
|--------|------|------|--------|
| id | Long | 模版ID | `8584` |
| name | String | 模版名称 | `佣金30模版` |
| area | Double | 面积(㎡) | `56.0` |
| rent | String | 租金(元/月) | `560` |
| roomDetail | String | 户型描述 | `2室1厅1厨1卫` |

---

## 9. 批量添加公寓

### POST `/core/web/apartment/addMore`

**请求头**：
```
Authorization: Bearer <jwt_token>
Content-Type: application/json; charset=utf-8
```

**请求参数** (JSON body)：

| 参数名 | 类型 | 必填 | 说明 | 示例值 |
|--------|------|------|------|--------|
| provinceId | String | 是 | 省份ID | `1` |
| provinceName | String | 是 | 省份名称 | `上海市` |
| cityId | String | 是 | 城市/区ID | `6758` |
| cityName | String | 是 | 城市/区名称 | `奉贤区` |
| communityId | String | 是 | 小区ID | `3672` |
| communityName | String | 是 | 小区名称 | `新北路96弄小区` |
| block | String | 是 | 楼幢 | `1幢` |
| unit | String | 是 | 单元 | `1单元` |
| elevator | Boolean | 是 | 是否有电梯 | `true` |
| totalFloor | Integer | 是 | 总楼层数 | `3` |
| managementList | Array | 是 | 楼层管理配置 | `[...]` |

**managementList 数组元素结构**：

| 参数名 | 类型 | 必填 | 说明 | 示例值 |
|--------|------|------|------|--------|
| floor | Integer | 是 | 楼层号 | `1` |
| select | Boolean | 是 | 是否选中 | `true` |
| edit | Boolean | 是 | 是否编辑模式 | `false` |
| num | Integer | 是 | 每层房间数 | `4` |
| sum | Array | 是 | 房间序号配置 | `[{value:1,label:false},...]` |
| list | Array | 是 | 该层房间列表 | `[...]` |

**sum 数组元素结构**：

| 参数名 | 类型 | 说明 | 示例值 |
|--------|------|------|--------|
| value | Integer | 房间序号值 | `1` |
| label | Boolean | 是否标记 | `false` |

**list 数组元素结构**：

| 参数名 | 类型 | 必填 | 说明 | 示例值 |
|--------|------|------|------|--------|
| name | String | 是 | 房间名称 | `A1001` |
| templateId | Long | 是 | 使用的模版ID | `10388` |
| templateName | String | 是 | 模版名称 | `佣金30模版-副本` |

---

### 请求示例（简化版）

```json
{
  "provinceId": "1",
  "provinceName": "上海市",
  "cityId": "6758",
  "cityName": "奉贤区",
  "communityId": "3672",
  "communityName": "新北路96弄小区",
  "block": "1幢",
  "unit": "1单元",
  "elevator": true,
  "totalFloor": 3,
  "managementList": [
    {
      "floor": 1,
      "select": true,
      "edit": false,
      "num": 4,
      "sum": [
        {"value": 1, "label": false},
        {"value": 2, "label": false},
        {"value": 3, "label": false},
        {"value": 4, "label": false}
      ],
      "list": [
        {"name": "A1001", "templateId": 10388, "templateName": "佣金30模版-副本"},
        {"name": "A1002", "templateId": 10388, "templateName": "佣金30模版-副本"},
        {"name": "A1003", "templateId": 10388, "templateName": "佣金30模版-副本"},
        {"name": "A1004", "templateId": 10388, "templateName": "佣金30模版-副本"}
      ]
    },
    {
      "floor": 2,
      "select": true,
      "edit": false,
      "num": 4,
      "sum": [
        {"value": 1, "label": false},
        {"value": 2, "label": false}
      ],
      "list": [
        {"name": "A2001", "templateId": 10388, "templateName": "佣金30模版-副本"},
        {"name": "A2002", "templateId": 10388, "templateName": "佣金30模版-副本"}
      ]
    }
  ]
}
```

**响应结构** (JSON)：

```json
{
  "success": true,
  "message": "成功"
}
```

**响应字段说明**：

| 字段名 | 类型 | 说明 |
|--------|------|------|
| success | Boolean | 请求是否成功 |
| message | String | 响应消息 |

---

## 10. 其他辅助接口

### 房源校验（合租）

### POST `/core/checkHouseIndexPlus`

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| id | Long | 是 | 合租房父ID |

**响应结构**：

```json
{
  "success": true,
  "message": "成功",
  "data": {
    "id": 2749274,
    "name": "9幢1单元101室",
    "communityName": "合嵣悦府东区",
    "communityId": 395875,
    "districtName": "余杭区",
    "area": 87.0,
    "rent": "301.00",
    "houseStatus": {"message": "未出租", "name": "WAITING_RENT"},
    "roomNumber": 2,
    "kitchenNumber": 1,
    "toiletNumber": 1,
    "livingRoomNumber": 1,
    "sonHouse": [
      {
        "id": 2749278,
        "name": "9幢1单元1011",
        "houseStatus": {"message": "未出租", "name": "WAITING_RENT"},
        "meterCotenancyAddFroms": [],
        "weterCotenancyAddForms": []
      }
    ]
  }
}
```

---

### 房源索引查询（整租）

### GET `/core/app/house/getHouseIndex`

**Query 参数**：

| 参数名 | 类型 | 说明 |
|--------|------|------|
| id | Long | 房源ID |

**响应结构**：

```json
{
  "success": true,
  "message": "成功",
  "data": {
    "commission": "50",
    "openRate": false,
    "rate": "100",
    "click": false,
    "cityName": "杭州市",
    "districtName": "滨江区",
    "communityName": "中天·官河锦庭",
    "communityId": 362440,
    "cityId": 561,
    "provinceId": 19,
    "block": "9幢",
    "videoUrl": "",
    "unit": "1单元",
    "name": "9002室",
    "area": 87.0,
    "floor": 1,
    "totalFloor": 1,
    "rent": "320.00",
    "roomNumber": 2,
    "livingRoomNumber": 1,
    "kitchenNumber": 1,
    "toiletNumber": 1,
    "orientation": "朝南",
    "waterPay": true,
    "rentType": "WHOLE",
    "parentId": 0,
    "renovation": "SIMPLE_DECORATION"
  }
}
```

---

### 设备计价配置

### GET `/core/manual/selectDevicePriceHandle`

**响应结构**：

```json
{
  "success": true,
  "message": "成功",
  "data": {
    "type": "HUI_KUAN_DAY",
    "initPrice": "0.00"
  }
}
```

---

## 完整 API 端点汇总表

| # | 方法 | 路径 | 功能 |
|---|------|------|------|
| 1 | POST | `/core/app/houseManageExt/accurateSearch` | 小区精确搜索 |
| 2 | POST | `/core/cotenancyHouse/list` | 合租房列表查询 |
| 3 | GET | `/core/wholeHouse/getBlock` | 合租栋座获取 |
| 4 | POST | `/core/houseAdd/wholeAdd` | 新增整租房源 |
| 5 | POST | `/core/houseAdd/cotenancyAdd` | 新增合租房源 |
| 6 | POST | `/core/houseAdd/cotenancyHouseEdit` | 合租房分间编辑 |
| 7 | GET | `/core/app/house/getHouseIndex` | 整租房详情查询 |
| 8 | GET | `/core/app/house/getCotenancyHouseIndex` | 合租房详情查询 |
| 9 | POST | `/core/checkHouseIndexPlus` | 房源完整性校验 |
| 10 | POST | `/core/app/house/checkHouseIndexMoreHb` | 整房完整性校验 |
| 11 | POST | `/findhouse/houseCommissionConfig/save` | 佣金配置保存 |
| 12 | GET | `/core/app/house/provinceChoose` | 省份列表获取 |
| 13 | GET | `/core/app/house/cityChooseA` | 城市列表获取 |
| 14 | GET | `/core/web/template/choose` | 公寓模版列表 |
| 15 | POST | `/core/web/apartment/addMore` | 批量添加公寓 |
| 16 | GET | `/core/manual
