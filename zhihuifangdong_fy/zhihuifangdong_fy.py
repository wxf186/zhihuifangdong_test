#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
智慧房东 APP - 房源管理接口测试（fy）
仅负责加载和运行所有拆分测试文件，统一收集结果
token 由 config.token_manager 统一管理（从 sy/login.py 持久化）
"""

import sys
import time
import os
from datetime import datetime
sys.path.insert(0, os.path.normpath(os.path.join(os.path.dirname(__file__), '..')))

from base_tester import *
from config.report_generator import TEST_NAME_MAP

# 本地耗时记录器
def _record_duration(ms: int):
    if TEST_RESULTS:
        TEST_RESULTS[-1]["duration"] = ms

# 本次测试的分组标识（用于报告分类）
TEST_GROUP = "fy"

# ==================== 加载所有拆分测试 ====================
# 按执行顺序（无 login，token 统一从 token_manager 获取）
import test_accurate_search as t02
import test_cotenancy_list as t03
import test_get_block as t04
import test_whole_add as t05
import test_cotenancy_add as t06
import test_cotenancy_house_edit as t07
import test_get_house_index as t08
import test_get_cotenancy_house_index as t09
import test_check_house_index_plus as t10
import test_house_commission_config_save as t11
import test_province_choose as t12
import test_city_choose as t13
import test_show_landlord_community as t14
import test_get_community as t15
import test_select_device_price as t16
import test_template_choose as t17
import test_add_more as t18

# 所有测试类（按执行顺序，login 已移除）
TEST_CLASSES = [
    t02.TestSearch,
    t03.TestCotenancy,
    t04.TestCotenancy,
    t05.TestHouseAdd,
    t06.TestHouseAdd,
    t07.TestHouseAdd,
    t08.TestHouseIndex,
    t09.TestHouseIndex,
    t10.TestHouseIndex,
    t11.TestCommission,
    t12.TestDistrict,
    t13.TestDistrict,
    t14.TestCommunity,
    t15.TestCommunity,
    t16.TestDevice,
    t17.TestApartment,
    t18.TestApartment,
]


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="智慧房东 APP 房源管理接口测试（fy）")
    parser.add_argument("--env", default="test2", choices=["test2", "formal"],
                        help="运行环境: test2 (默认) 或 formal")
    parser.add_argument("--output-json", action="store_true", help="仅输出JSON不生成报告")
    args = parser.parse_args()

    import config.api_config as api_config
    if args.env != "test2":
        api_config.set_env(args.env)

    print("\n" + "="*60)
    print(f"🔐 获取Token... [环境: {api_config.ACTIVE_ENV}]")
    print(f"   域名: {get_base_url()}")
    print("="*60)

    # 统一从 token_manager 获取（自动加载缓存或重新登录）
    from config.token_manager import get_or_login_token
    token_info = get_or_login_token(api_config.ACTIVE_ENV)
    set_token(token_info["token"])
    USER_ID = token_info.get("user_id")
    print(f"✅ Token获取成功，用户ID: {USER_ID}")

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
                method = getattr(instance, method_name)
                METHOD_RECORDED[0]["flag"] = False
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
                        print(f"❌ {TEST_NAME_MAP.get(method_name, method_name)} 失败: {str(e)}")

    END_TIME = datetime.now()
    print(f"\n{'='*60}")
    print(f"📊 运行结果: {passed} 通过, {failed} 失败")
    print(f"{'='*60}")

    def _get_report_path(prefix: str) -> str:
        """生成带日期的报告路径：D:/cc/APP/reports/fy-2026-05-13.html"""
        reports_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'reports')
        os.makedirs(reports_dir, exist_ok=True)
        date_str = datetime.now().strftime("%Y-%m-%d_%H%M")
        return os.path.join(reports_dir, f"{prefix}-{date_str}.html")

    report_path = _get_report_path("fy")

    print("\n📊 生成测试报告...")
    if args.output_json:
        json_path = os.path.join(os.path.dirname(__file__), "_fy_results.json")
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
