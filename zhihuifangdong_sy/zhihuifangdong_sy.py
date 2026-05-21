#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
智慧房东 APP - 接口自动化测试脚本（sy）
仅负责加载和运行所有拆分测试文件，统一收集结果
"""

import sys
import time
import os
from datetime import datetime
sys.path.insert(0, os.path.normpath(os.path.join(os.path.dirname(__file__), '..')))

from base_tester import *
import base_tester as base_tester_module
from config.report_generator import TEST_NAME_MAP

# 本地耗时记录器（给最近一条 TEST_RESULTS 设置 duration）
def _record_duration(ms: int):
    if TEST_RESULTS:
        TEST_RESULTS[-1]["duration"] = ms

# 本次测试的分组标识（用于报告分类）
TEST_GROUP = "sy"

# ==================== 加载所有拆分测试 ====================
# 按执行顺序排列（login 需最先）
import test_login as t01
import test_user_info as t02
import test_self_menu_with_role as t03
import test_self_menu as t04
import test_self_menu_for_new as t05
import test_have_guide as t06
import test_have_iot as t07
import test_commission_bear as t08
import test_certificate_expiration_remind as t09
import test_query_user_guidance as t10
import test_get_simple_rent as t11
import test_new_house_data_up as t12
import test_count_waiting_read_message as t13
import test_meter_of_water_total as t14
import test_my_contract_num as t15
import test_my_contract_approval_num as t16
import test_contract_approval_list as t17
import test_banner_pic_more as t18
import test_click_pic as t19
import test_click_pic_more as t20
import test_platform_pic as t21
import test_query_version_info as t22
import test_get_door_lock_status_count as t23
import test_get_door_lock_list as t24
import test_flux_remind_window as t25
import test_flux_remind_window_overdue as t26
import test_get_bind_card_fail_pop as t27
import test_zd_bank_migrate_admin as t28
import test_support_tourist as t29
import test_add_mec_address as t30
import test_water_meter_list as t31
import test_meter_list as t32

# 所有测试类（按执行顺序）
TEST_CLASSES = [
    t01.TestAuth,
    t02.TestUserInfo,
    t03.TestUserInfo,
    t04.TestUserInfo,
    t05.TestUserInfo,
    t06.TestUserInfo,
    t07.TestUserInfo,
    t08.TestUserInfo,
    t09.TestUserInfo,
    t10.TestUserInfo,
    t11.TestHouse,
    t12.TestHouse,
    t13.TestHouse,
    t14.TestHouse,
    t15.TestContract,
    t16.TestContract,
    t17.TestContract,
    t18.TestActivity,
    t19.TestActivity,
    t20.TestActivity,
    t21.TestActivity,
    t22.TestActivity,
    t23.TestDevice,
    t24.TestDevice,
    t25.TestMeter,
    t26.TestMeter,
    t27.TestBindCard,
    t28.TestBindCard,
    t29.TestHousePromotion,
    t30.TestFeign,
    t31.TestMeter,
    t32.TestMeter,
]

# login 已在 login fixture 中记录
SKIP_LOGIN_RECORD = True


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="智慧房东 APP 接口测试（sy）")
    parser.add_argument("--env", default="test2", choices=["test2", "formal"],
                        help="运行环境: test2 (默认) 或 formal")
    parser.add_argument("--output-json", action="store_true", help="仅输出JSON不生成报告")
    args = parser.parse_args()

    import config.api_config as api_config
    if args.env != "test2":
        api_config.set_env(args.env)

    from config.api_config import USERS
    current_user = USERS[api_config.ACTIVE_ENV]
    login_payload = {
        "username": current_user["username"],
        "password": current_user["password"],
    }

    print("\n" + "="*60)
    print(f"🔐 开始登录认证... [环境: {api_config.ACTIVE_ENV}]")
    print(f"   域名: {get_base_url()}")
    print(f"   账号: {current_user['username']}")
    print("="*60)
    METHOD_RECORDED[0]["flag"] = False

    login_response = api_request(
        "POST",
        "/auth/auth/apploginMultipleRole",
        need_auth=False,
        data=login_payload,
        timeout=API_CONFIG["login_timeout"]
    )
    print(f"登录响应: {json.dumps(login_response, ensure_ascii=False, indent=2)}")
    if login_response.get("success") and login_response.get("data", {}).get("token"):
        token = login_response["data"]["token"]
        set_token(token)
        try:
            payload = token.split('.')[1]
            payload += '=' * (4 - len(payload) % 4)
            decoded = json.loads(base64.b64decode(payload))
            USER_ID = decoded.get("id")
        except Exception as e:
            print(f"⚠️ JWT解码失败: {e}")
            USER_ID = None
        base_tester_module.LOGIN_RESPONSE = login_response
        print(f"✅ Token获取成功")
        print(f"👤 用户ID: {USER_ID}")
    else:
        # 登录失败也打印提示，然后继续（不走 sys.exit，避免丢失请求数据）
        print(f"❌ 登录失败: {login_response.get('message', '未知错误')}")
        # 注意：不要手动 record_result("test_01_login_success", ...)，test_01 自己会记录
        # 不 sys.exit(1)，让脚本继续运行（后续测试若无 token 会自然失败）

    START_TIME = datetime.now()
    print("\n" + "="*60)
    print("📋 开始运行测试用例...")
    print("="*60)

    passed = 0
    failed = 0

    for cls in TEST_CLASSES:
        instance = cls()
        for method_name in dir(instance):
            if method_name.startswith("test_"):
                if cls.__name__ == "TestAuth" and method_name == "test_01_login":
                    print(f"⏭️ login 已于登录时记录，跳过")
                    continue
                METHOD_RECORDED[0]["flag"] = False
                method = getattr(instance, method_name)
                _start = time.time()
                try:
                    method()
                    _elapsed = int((time.time() - _start) * 1000)
                    _record_duration(_elapsed)
                    passed += 1
                except Exception as e:
                    failed += 1
                    exc_response = getattr(e, 'response', None)
                    if not METHOD_RECORDED[0]["flag"]:
                        _elapsed = int((time.time() - _start) * 1000)
                        api_path = getattr(e, 'api_path', '') or CURRENT_API_PATH or ""
                        _r = exc_response if exc_response else {"success": False, "message": str(e)}
                        record_result(
                            method_name,
                            api_path,
                            _r,
                            "FAILED",
                            TEST_GROUP
                        )
                        _record_duration(_elapsed)

    END_TIME = datetime.now()
    print(f"\n{'='*60}")
    print(f"📊 运行结果: {passed} 通过, {failed} 失败")
    print(f"{'='*60}")

    def _get_report_path(prefix: str) -> str:
        """生成带日期的报告路径"""
        reports_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'reports')
        os.makedirs(reports_dir, exist_ok=True)
        date_str = datetime.now().strftime("%Y-%m-%d_%H%M")
        return os.path.join(reports_dir, f"{prefix}-{date_str}.html")

    report_path = _get_report_path("sy")

    print("\n📊 生成测试报告...")
    if args.output_json:
        json_path = os.path.join(os.path.dirname(__file__), "_sy_results.json")
        with open(json_path, "w", encoding="utf-8") as _f:
            json.dump(TEST_RESULTS, _f, ensure_ascii=False, indent=2)
        print(f"📄 JSON已保存: {json_path}")
        sys.exit(0)

    generate_report(
        TEST_RESULTS,
        output_path=report_path,
        start_time=START_TIME.strftime("%Y-%m-%d %H:%M:%S"),
        end_time=END_TIME.strftime("%Y-%m-%d %H:%M:%S"),
    )
    print(f"✅ 报告已生成: {report_path}")
    print(f"   双击或浏览器打开: file://{os.path.abspath(report_path)}")
