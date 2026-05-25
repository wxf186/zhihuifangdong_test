#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
智慧房东 APP - /core/app/houseManageExt/showLandLordCommunity 接口测试
"""

import sys
import os
sys.path.insert(0, os.path.normpath(os.path.join(os.path.dirname(__file__), '..')))

import base_tester

TEST_GROUP = "fy"
class TestCommunity:
    """/core/app/houseManageExt/showLandLordCommunity"""

    def test_16_show_landlord_community(self):
        """房东小区列表"""
        print("\n📋 测试房东小区列表...")
        response = base_tester.api_request(
            "GET",
            "/core/app/houseManageExt/showLandLordCommunity",
            params={
                "current": 1,
                "size": 10000,
                "cityName": "奉贤区",
                "provinceId": 1,
                "provinceName": "上海市"
            }
        )
        print(f"响应: {base_tester.json.dumps(response, ensure_ascii=False, indent=2)[:300]}")
        base_tester.validate_response(response, allow_success_false=True)
        print(f"✅ 房东小区列表获取成功")
        base_tester.record_result("test_16_show_landlord_community", "/core/app/houseManageExt/showLandLordCommunity", response, "PASSED", group=TEST_GROUP)



if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="智慧房东 APP 接口测试")
    parser.add_argument("--env", default="test2", choices=["test2", "formal"],
                        help="运行环境: test2 (默认) 或 formal")
    parser.add_argument("--output-json", action="store_true", help="仅输出JSON不生成报告")
    args = parser.parse_args()

    import config.api_config as api_config
    if args.env != "test2":
        api_config.set_env(args.env)

    # 统一从 token_manager 获取 token
    from config.token_manager import get_or_login_token
    token_info = get_or_login_token(api_config.ACTIVE_ENV)
    base_tester.set_token(token_info["token"])

    instance = TestCommunity()
    method = getattr(instance, "test_16_show_landlord_community")
    METHOD_RECORDED = False
    try:
        method()
        print("\n✅ " + "test_16_show_landlord_community" + " 执行通过")
    except Exception as e:
        exc_response = getattr(e, 'response', None)
        api_path_val = getattr(e, 'api_path', '') or base_tester.CURRENT_API_PATH or ""
        base_tester.record_result(
            "test_16_show_landlord_community",
            api_path_val,
            exc_response if exc_response else {"success": False, "message": str(e)},
            "FAILED", group=TEST_GROUP)
        print("\n❌ " + "test_16_show_landlord_community" + " 执行失败: " + str(e))

    if args.output_json:
        json_path = os.path.join(os.path.dirname(__file__), "_results.json")
        with open(json_path, "w", encoding="utf-8") as _f:
            base_tester.json.dump(base_tester.TEST_RESULTS, _f, ensure_ascii=False, indent=2)
        print("📄 JSON已保存: " + json_path)
    else:
        config_dir = os.path.join(os.path.dirname(__file__), '..', 'config')
        report_path = os.path.join(config_dir, "report.html")
        base_tester.generate_report(base_tester.TEST_RESULTS, output_path=report_path)
        print("\n✅ 报告已生成: " + report_path)

