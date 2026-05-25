# zhihuifangdong_test 测试项目规范

## 项目结构

```
zhihuifangdong_test/                          # 智慧房东 APP 接口测试项目根目录
├── base_tester.py                            # 公共测试基类（全局状态、核心工具函数）
├── zhihuifangdong_all.py                     # 合并主入口（串行执行 sy + fy，生成统一 HTML 报告）
├── requirements.txt                          # Python 依赖（requests / urllib3 等）
├── NOTES.md                                  # 项目规范文档
├── config/                                   # 共享配置目录
│   ├── __init__.py
│   ├── api_config.py                         # API 环境配置（formal / test2，USERS 字典）
│   ├── report_generator.py                   # HTML 报告生成器（TEST_NAME_MAP、二级分组卡片/表格）
│   ├── token_manager.py                      # token 统一读写（get_or_login_token / save_token）
│   └── sync_notes.py                        # 项目结构变更检测脚本（对比快照，追加到 NOTES.md 和 work_log）
├── tokens/                                   # token 缓存目录
│   └── test2.json                            # test2 环境 token 缓存（JSON 格式）
├── reports/                                  # HTML 报告归档目录
│   ├── sy-YYYY-MM-DD_HHMM.html               # sy 单独运行报告
│   ├── fy-YYYY-MM-DD_HHMM.html              # fy 单独运行报告
│   └── all-YYYY-MM-DD_HHMM.html             # 合并报告（主要使用）
├── work_logs/                               # 工作日志目录
│   ├── create_log.py                         # 每日日志创建脚本（systemd timer 触发）
│   ├── 2026-05-18.md                        # 历史工作日志
│   └── 2026-05-19.md                        # 当天工作日志
├── zhihuifangdong_sy/                       # 室友管理接口测试（TEST_GROUP="sy"，~39 个用例）
│   ├── zhihuifangdong_sy.py                 # sy 主入口：登录 fixture + 遍历所有 test_*.py
│   ├── _sy_results.json                     # 上次 sy 运行结果 JSON
│   ├── test_login.py                        # 登录接口（10 个用例：正常登录、密码错误、并发等）
│   ├── test_user_info.py                    # 用户信息
│   ├── test_self_menu.py                    # 个人菜单
│   ├── test_self_menu_with_role.py          # 带角色的个人菜单
│   ├── test_self_menu_for_new.py            # 新用户个人菜单
│   ├── test_have_guide.py                   # 是否有引导
│   ├── test_have_iot.py                     # 是否有 IoT 设备
│   ├── test_commission_bear.py              # 佣金承担
│   ├── test_certificate_expiration_remind.py # 证书到期提醒
│   ├── test_query_user_guidance.py          # 查询用户引导
│   ├── test_get_simple_rent.py              # 获取简化租金
│   ├── test_new_house_data_up.py            # 新房源数据上传
│   ├── test_count_waiting_read_message.py  # 待读消息计数
│   ├── test_meter_of_water_total.py        # 水表总量
│   ├── test_add_mec_address.py              # 添加 MEC 地址
│   ├── test_banner_pic_more.py              # 横幅图片更多
│   ├── test_click_pic.py                   # 点击图片
│   ├── test_click_pic_more.py               # 点击图片更多
│   ├── test_contract_approval_list.py      # 合同审批列表
│   ├── test_flux_remind_window.py           # 流量提醒窗口
│   ├── test_flux_remind_window_overdue.py  # 流量提醒窗口逾期
│   ├── test_get_bind_card_fail_pop.py      # 绑卡失败弹窗
│   ├── test_get_door_lock_list.py          # 门锁列表
│   ├── test_get_door_lock_status_count.py  # 门锁状态计数
│   ├── test_meter_list.py                  # 电表列表
│   ├── test_my_contract_approval_num.py     # 我的合同审批数量
│   ├── test_my_contract_num.py              # 我的合同数量
│   ├── test_platform_pic.py                 # 平台图片
│   ├── test_query_version_info.py          # 查询版本信息
│   ├── test_support_tourist.py             # 支持游客
│   ├── test_water_meter_list.py            # 水表列表
│   ├── test_zd_bank_migrate_admin.py       # 银行迁移管理员
│   └── report-2026-05-07-zhihuifangdong_sy.md  # 历史报告文档
└── zhihuifangdong_fy/                       # 房源管理接口测试（TEST_GROUP="fy"，~17 个用例）
    ├── zhihuifangdong_fy.py                # fy 主入口：遍历所有 test_*.py（无独立登录）
    ├── _fy_results.json                     # 上次 fy 运行结果 JSON
    ├── test_accurate_search.py              # 精确搜索
    ├── test_add_more.py                    # 添加更多
    ├── test_check_house_index_plus.py       # 房源指数检查
    ├── test_city_choose.py                  # 城市选择
    ├── test_cotenancy_add.py               # 合租添加
    ├── test_cotenancy_house_edit.py         # 合租房编辑
    ├── test_cotenancy_list.py              # 合租列表
    ├── test_get_block.py                   # 获取板块
    ├── test_get_community.py               # 获取小区
    ├── test_get_cotenancy_house_index.py   # 合租房指数
    ├── test_get_house_index.py             # 获取房源指数
    ├── test_house_commission_config_save.py # 房源佣金配置保存
    ├── test_province_choose.py             # 省份选择
    ├── test_select_device_price.py         # 选择设备价格
    ├── test_show_landlord_community.py     # 显示房东小区
    ├── test_template_choose.py             # 模板选择
    ├── test_whole_add.py                   # 整租添加
    ├── _probe_traceback.py                 # traceback 探测脚本（调试用）
    └── 创建合同接口文档-2026-05-12.md       # 接口文档
```

## 目录与文件功能说明

| 路径 | 类型 | 功能说明 |
|---|---|---|
| `base_tester.py` | 文件 | 公共测试基类：定义 `TEST_RESULTS`、`LOGIN_RESPONSE`、`METHOD_RECORDED`、`record_result()`、`validate_response()`、`api_request()`、`get_headers()` 等核心组件。登录响应保存在 `base_tester.LOGIN_RESPONSE`（供 test_login.py 通过 `import base_tester` 访问）。|
| `zhihuifangdong_all.py` | 文件 | 合并主入口：通过 `subprocess` 串行执行 sy.py 和 fy.py，合并两个 JSON 结果后调用 `report_generator.generate_report()` 生成统一 HTML 报告。|
| `zhihuifangdong_sy/zhihuifangdong_sy.py` | 文件 | sy 主入口：包含 `before_all` fixture（登录认证 + token 缓存），登录成功后 `base_tester_module.LOGIN_RESPONSE = login_response` 写入全局，遍历所有 `test_*.py` 执行测试。|
| `zhihuifangdong_sy/test_login.py` | 文件 | 登录接口测试（10 个用例）：正常登录、用户名不存在、密码错误、空用户名、空密码、密码过短、未注册账号、并发登录禁用/不禁用、禁用账号（已注释）。`test_01_login_success` 通过 `import base_tester; base_tester.LOGIN_RESPONSE` 访问 fixture 写入的登录响应。|
| `zhihuifangdong_fy/zhihuifangdong_fy.py` | 文件 | fy 主入口：无独立登录逻辑，通过 `token_manager.get_or_login_token()` 复用 sy 缓存的 token，遍历所有 `test_*.py` 执行测试。|
| `config/api_config.py` | 文件 | API 环境配置：定义 `ENVIRONMENTS`（test2/formal）、`ACTIVE_ENV`、`set_env()`、`get_base_url()`、`USERS`（用户名密码字典）等。|
| `config/report_generator.py` | 文件 | HTML 报告生成器：含 `TEST_NAME_MAP`（用例 ID → 中文名称映射）、`generate_report()`、`src_disp()`（来源显示）、card/modal/table 模板。|
| `config/token_manager.py` | 文件 | token 统一管理：`get_or_login_token()` 优先读缓存，缓存失效时自动重新登录；`save_token()` 持久化到 `tokens/{env}.json`。|
| `config/sync_notes.py` | 文件 | 项目结构变更检测：扫描关键文件（test_*.py、base_tester.py 等）计算 MD5 快照，对比上次记录，检测到变更时追加到 `NOTES.md` 和当日 `work_log`。|
| `tokens/test2.json` | 文件 | test2 环境 token 缓存文件，含 token 字符串和过期时间 exp。|
| `reports/` | 目录 | HTML 报告归档：按日期+时分命名，`all-YYYY-MM-DD_HHMM.html` 为主要使用的合并报告。|
| `work_logs/` | 目录 | 工作日志目录：每日自动/手动创建 `YYYY-MM-DD.md`，记录当天的工作内容和变更。|

## 报告归档

运行完成后报告自动归档到 `reports/` 文件夹，按日期+时分命名：

```
reports/
├── sy-2026-05-13_1720.html
├── fy-2026-05-13_1720.html
└── all-2026-05-13_1720.html      # 合并报告（主要使用）
```

## token 管理

- token 统一由 `config/token_manager.py` 管理
- sy fixture 是唯一登录入口，登录成功后 `base_tester_module.LOGIN_RESPONSE = login_response` 写入全局
- test_login.py 通过 `import base_tester; base_tester.LOGIN_RESPONSE` 访问登录响应
- fy 运行时通过 `get_or_login_token()` 复用缓存 token
- token 文件存放于 `tokens/test2.json`

## 报告格式规范

### 表格列顺序

| # | 状态 | 用例名称 | 来源 | 接口 | 耗时 | 响应内容 | 信息 |

### 用例来源分组显示

报告按 `group` 字段分为两级分组：
- `zhihuifangdong_sy`：室友管理接口（sy 分组）
- `zhihuifangdong_fy`：房源管理接口（fy 分组）

卡片视图和列表视图均按分组显示，`group` 字段由 `record_result(..., group=TEST_GROUP)` 传入。

### 测试名称映射（TEST_NAME_MAP）

报告中显示的用例名称通过 `TEST_NAME_MAP` 映射为中文名称，需在 `report_generator.py` 中维护。

## METHOD_RECORDED 机制

### 作用

防止同一测试方法被重复记录到 `TEST_RESULTS`。每个测试方法执行前将 `METHOD_RECORDED[0]["flag"]` 设为 `False`，`record_result` 调用后设为 `True`。

### 实现方式（避免 global 声明问题）

由于 Python 3.11 对 `global` 声明在嵌套 `for` 循环（`try` 块内）中有作用域限制，使用可变容器避免：

```python
# base_tester.py
METHOD_RECORDED = [{"flag": False}]  # 可变容器，规避 global 声明问题

# 测试方法内
METHOD_RECORDED[0]["flag"] = False    # 重置（注意：不能用 = 重新赋值，会创建新局部变量）

# record_result() 内部
METHOD_RECORDED[0]["flag"] = True     # 标记已记录
```

### 注意事项

- `from base_tester import *` 不会导入下划线开头的私有函数（如 `_record_duration`）
- 如需在测试方法内直接操作 duration，应直接修改 `TEST_RESULTS[-1]["duration"]`
- `record_result` 已内置 `"group"` 字段

## LOGIN_RESPONSE 跨模块共享机制

### 背景

sy.py fixture 登录成功后，需要让 test_login.py 中的 `test_01_login_success` 访问到登录响应。

### 问题

`say.py` 中 `from base_tester import *` 会将 `LOGIN_RESPONSE` 绑定到 sy.py 的**本地命名空间**（值为 `None` 的拷贝）。后续在 sy.py 里 `global LOGIN_RESPONSE; LOGIN_RESPONSE = login_response` 只修改本地副本，不影响 `base_tester.LOGIN_RESPONSE`。

test_login.py 同样 `from base_tester import *`，导入的也是自己的本地拷贝，始终为 `None`。

### 解决方案

```python
# sy.py
import base_tester as base_tester_module   # 导入 base_tester 模块本身

# fixture 登录成功后：
base_tester_module.LOGIN_RESPONSE = login_response   # 写入模块变量

# test_login.py
import base_tester   # 不从 base_tester import *，改为 import base_tester

# test_01 中：
validate_response(base_tester.LOGIN_RESPONSE)   # 通过模块对象访问
record_result(..., base_tester.LOGIN_RESPONSE, ...)  # 传入响应对象
```

## 已知问题与修复记录

### 2026-05-19

#### 1. test_01_login_success 失败（LOGIN_RESPONSE 为空）

**问题**：fixture 登录成功（`✅ Token获取成功` 打印），但 `test_01_login_success` 报错 `"LOGIN_RESPONSE 为空（fixture登录失败）"`。

**根因**：`from base_tester import *` 在各模块创建独立的本地绑定，`global LOGIN_RESPONSE` + 赋值只修改本地副本，两边各是不同变量。

**修复**：
- sy.py：`import base_tester as base_tester_module`，fixture 中 `base_tester_module.LOGIN_RESPONSE = login_response`
- test_login.py：`import base_tester`（不再 `from base_tester import *`），访问改为 `base_tester.LOGIN_RESPONSE`

#### 2. test_01 双重记录

**问题**：fixture else 分支手动调用 `record_result("test_01_login_success", ...)`，test_01 自己也会调用，导致重复记录。

**修复**：移除 else 分支中的手动 `record_result` 调用，test_01 自身会处理记录。

#### 3. sys.exit(1) 导致进程崩溃

**问题**：fixture 登录失败时 `sys.exit(1)` 直接退出，`test_01` 的请求数据无法记录。

**修复**：移除 `sys.exit(1)`，登录失败也继续运行（后续测试若无 token 会自然失败）。

#### 4. source_file 显示为 base_tester.py

**问题**：traceback 中 `base_tester.py` 绝对路径含 `"zhihuifangdong"` 关键字，被误匹配为源码文件。

**修复**：跳过条件增加 `or fname.endswith("base_tester.py")`。

#### 5. fy 用例 source_file 为空

**问题**：fy.py 入口通过 `subprocess` 运行，traceback 无法正确获取源码文件。

**修复**：在 fy 入口所有测试方法最后统一补录一次结果，`source_file` 传入空字符串，依赖 `record_result` 自动从 traceback 获取。

### 2026-05-15

#### 1. 用例来源分组不显示（已修复）

**问题**：`record_result` 接收 `group` 参数但未写入 `TEST_RESULTS`。

**修复**：`record_result` 的 `TEST_RESULTS.append` 添加 `"group": group` 字段。

#### 2. test_25 / test_26 duration 为 None（已修复）

**根因**：`_record_duration` 是下划线开头私有函数，`from base_tester import *` 不会导入它，`NameError` 导致异常处理链断裂。

**修复**：将 `finally` 块改为直接操作 `TEST_RESULTS[-1]["duration"]`。

#### 3. 重复用例记录问题（已修复）

**根因**：`METHOD_RECORDED = False` 在嵌套 `for` 循环中赋值时没有 `global` 声明，导致遮蔽全局变量。

**修复**：改用 `METHOD_RECORDED[0]["flag"] = False/True` 可变容器方案。

### 2026-05-20 项目变更

_自动扫描于 2026-05-20 20:20_


无变更。


### 2026-05-21 项目变更

_自动扫描于 2026-05-21 14:41_

  ~ 修改: `NOTES.md`
  ~ 修改: `config/sync_notes.py`
