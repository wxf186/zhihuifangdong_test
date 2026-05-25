# 创建合同接口 - 测试覆盖度复核报告

**复核日期**: 2026-05-21
**接口文档**: 创建合同接口文档-2026-05-12.md
**测试框架**: Python + requests
**评审人**: QA工程师

---

## 一、接口清单与覆盖状态

| # | 接口路径 | 方法 | 文档章节 | 测试文件 | 覆盖状态 |
|---|---------|------|---------|---------|---------|
| 1 | /core/app/houseManageExt/accurateSearch | POST | 3.1 | test_accurate_search.py | 部分覆盖 |
| 2 | /core/wholeHouse/getBlock | GET | 3.2 | test_get_block.py | 仅COTENANCY |
| 3 | /core/cotenancyHouse/list | POST | 3.3 | test_cotenancy_list.py | 仅基础分页 |
| 4 | /core/houseAdd/wholeAdd | POST | 3.4 | test_whole_add.py | 成功路径 |
| 5 | /core/app/house/checkHouseIndexMoreHb | POST | 3.5 | **无** | **未覆盖** |
| 6 | /findhouse/houseCommissionCofig/save | POST | 3.6 | test_house_commission_config_save.py | **参数错误** |
| 7 | /core/houseAdd/cotenancyAdd | POST | 3.7 | test_cotenancy_add.py | 成功路径 |
| 8 | /core/houseAdd/cotenancyHouseEdit | POST | 3.8 | test_cotenancy_house_edit.py | 硬编码parentId |
| 9 | /core/checkHouseIndexPlus | POST | 3.9 | test_check_house_index_plus.py | 硬编码ID |
| 10 | /core/web/template/choose | GET | 3.10 | test_template_choose.py | 成功路径 |
| 11 | /core/web/apartment/addMore | POST | 3.11 | test_add_more.py | 成功路径 |
| 辅助1 | /core/app/house/provinceChoose | GET | 4-3 | test_province_choose.py | 成功路径 |
| 辅助2 | /core/app/house/cityChooseA | GET | 4-4 | test_city_choose.py | 成功路径 |
| 辅助3 | /core/app/houseManageExt/showLandLordCommunity | GET | 4-5 | test_show_landlord_community.py | 成功路径 |
| 辅助4 | /core/app/house/getCommunity | POST | 4-6 | test_get_community.py | 成功路径 |
| 辅助5 | /core/app/house/getHouseIndex | GET | 4-1 | test_get_house_index.py | 硬编码ID |
| 辅助6 | /core/app/house/getCotenancyHouseIndex | GET | 4-2 | test_get_cotenancy_house_index.py | 硬编码ID |
| 辅助7 | /core/manual/selectDevicePriceHandle | POST | - | test_select_device_price.py | 成功路径 |

---

## 二、业务流程覆盖评估

### 2.1 整租流程
```
精准搜索小区 → 获取楼栋信息 → 添加整租房源 → 房源详情确认 → 设置佣金 → 提交合同
```
| 步骤 | 接口 | 覆盖情况 |
|-----|------|---------|
| 精准搜索小区 | accurateSearch | 部分(缺异常) |
| 获取楼栋信息 | getBlock | 仅COTENANCY |
| 添加整租房源 | wholeAdd | 成功路径 |
| 房源详情确认 | checkHouseIndexMoreHb | **未覆盖** |
| 设置佣金 | commissionConfig/save | **参数错误** |

**评估**: 有缺失，缺少整租详情确认和正确的佣金配置

### 2.2 合租流程
```
精准搜索小区 → 获取楼栋信息 → 筛选房源列表 → 添加合租房源 → 编辑合租房间 → 房源详情确认 → 提交合同
```
| 步骤 | 接口 | 覆盖情况 |
|-----|------|---------|
| 精准搜索小区 | accurateSearch | 部分 |
| 获取楼栋信息 | getBlock | 仅COTENANCY |
| 筛选房源列表 | cotenancyHouse/list | 仅基础分页 |
| 添加合租房源 | cotenancyAdd | 成功路径 |
| 编辑合租房间 | cotenancyHouseEdit | 硬编码ID |
| 房源详情确认 | checkHouseIndexPlus | 硬编码ID |

**评估**: 基本覆盖，但缺少筛选条件测试和异常场景

### 2.3 公寓流程
```
选择省市区 → 搜索小区 → 选择模板 → 添加公寓楼栋 → 提交合同
```
| 步骤 | 接口 | 覆盖情况 |
|-----|------|---------|
| 选择省市区 | provinceChoose/cityChoose | 已覆盖 |
| 搜索小区 | getCommunity/showLandLordCommunity | 已覆盖 |
| 选择模板 | template/choose | 已覆盖 |
| 添加公寓楼栋 | apartment/addMore | 成功路径 |

**评估**: 基本覆盖，无端到端流程测试

---

## 三、缺失测试点清单

### 3.1 严重问题(影响功能验证)

- [ ] **整租详情确认接口无测试**: `/core/app/house/checkHouseIndexMoreHb`
- [ ] **佣金配置接口参数错误**: 请求体与文档不符
- [ ] **getBlock只测了COTENANCY**: 缺少WHOLE类型测试

### 3.2 异常场景缺失

| 接口 | 缺失场景 |
|------|---------|
| accurateSearch | 空关键词、特殊字符、超长关键词、无效rentType |
| wholeAdd | 缺少必填参数、重复房源、面积0、租金0或负数 |
| cotenancyAdd | 必填参数缺失、rent为0或负数 |
| cotenancyHouseEdit | parentId不存在、house列表为空 |
| addMore | managementList为空、num为0、floor超范围 |
| commissionConfig | commissionType无效、日期范围错误 |

### 3.3 参数组合缺失

- [ ] cotenancyHouse/list: 朝向/状态/房号/关键词筛选
- [ ] wholeAdd: 三种支付方式(MONTH/SEASON/YEAR)
- [ ] commissionConfig: 固定金额vs固定比例、日期范围组合

### 3.4 边界值缺失

- [ ] 分页: current=0、size=0或负数、size极大值
- [ ] 金额: 0、最小值、极大值
- [ ] 面积: 0、负数

### 3.5 响应校验缺失

- [ ] 所有接口均未校验响应字段结构和类型
- [ ] 未校验枚举值有效性(如houseStatus.payMethod等)

### 3.6 并发测试缺失

- [ ] 同一房源并发添加
- [ ] 重复提交测试

---

## 四、补充测试用例(已创建)

文件: `test_supplementary_cases.py`

| 测试方法 | 类型 | 说明 |
|---------|------|------|
| test_accurate_search_empty_keyword | 异常 | 空关键词 |
| test_accurate_search_invalid_rent_type | 异常 | 无效rentType |
| test_accurate_search_whole_type | 补充 | 整租搜索 |
| test_whole_add_missing_required_params | 异常 | 缺少必填参数 |
| test_whole_add_rent_zero | 边界 | 租金为0 |
| test_whole_add_all_pay_methods | 参数组合 | 三种支付方式 |
| test_get_block_whole_type | 补充 | 整租楼栋查询 |
| test_get_block_invalid_type | 异常 | 无效type |
| test_cotenancy_list_with_filters | 参数组合 | 带筛选条件 |
| test_cotenancy_list_pagination_boundary | 边界 | 分页边界 |
| test_cotenancy_add_rent_zero | 边界 | 租金为0 |
| test_commission_fixed_amount | 补充 | 佣金-固定金额 |
| test_commission_fixed_ratio | 补充 | 佣金-固定比例 |
| test_commission_date_range | 补充 | 佣金-时间段 |
| test_check_house_index_more_hb | 补充 | 整租确认(新增) |
| test_check_house_index_invalid_id | 异常 | 无效ID |
| test_add_more_empty_management_list | 异常 | 空楼层列表 |
| test_add_more_zero_rooms | 边界 | 房间数为0 |
| test_accurate_search_response_structure | 响应校验 | 字段结构 |

---

## 五、总体评估

| 评估维度 | 评级 | 说明 |
|---------|------|------|
| 业务覆盖 | 基本完整 | 三个流程均有覆盖，但不完整 |
| 接口覆盖 | 部分覆盖 | 17个接口中3个有严重问题 |
| 异常场景 | **未覆盖** | 所有接口均无异常测试 |
| 边界值 | **未覆盖** | 分页/金额/面积等边界均无 |
| 参数组合 | **未覆盖** | 筛选/枚举/多状态均无 |
| 响应校验 | **未覆盖** | 无字段结构校验 |
| 并发测试 | **未覆盖** | 无任何并发测试 |

**综合评估**: 有缺失 (覆盖率约40%)

---

## 六、建议优先级

### P0 (必须修复)
1. 修复佣金配置接口参数错误
2. 新增整租详情确认接口测试
3. 补充getBlock的WHOLE类型测试

### P1 (建议补充)
4. 补充各接口异常场景(空值/无效值)
5. 补充参数组合测试(筛选/支付方式)
6. 补充响应字段校验

### P2 (可选)
7. 边界值测试
8. 并发测试
9. 端到端流程测试