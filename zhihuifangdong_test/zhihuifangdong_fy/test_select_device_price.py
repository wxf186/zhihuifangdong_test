#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
智慧房东 APP - /core/manual/selectDevicePriceHandle 接口测试
"""

import sys
import os
sys.path.insert(0, os.path.normpath(os.path.join(os.path.dirname(__file__), '..')))

import base_tester

TEST_GROUP = "fy"
class TestDevice:
    """/core/manual/selectDevicePriceHandle"""

    def test_18_select_device_price(self):
        """设备添加默认价格"""
        print("\n📋 测试设备价格查询...")
        response = base_tester.api_request(
            "GET",
            "/core/manual/selectDevicePriceHandle",
            params={"type": 1}
        )
        print(f"响应: {base_tester.json.dumps(response, ensure_ascii=False, indent=2)}")
        status = "PASSED" if response.get("success") else "FAILED"
        base_tester.record_result("test_18_select_device_price", "/core/manual/selectDevicePriceHandle", response, status, group=TEST_GROUP)
        if not response.get("success"):
            e = AssertionError(f"业务失败: {response.get('message', '未知错误')}")
            e.response = response
            e.api_path = "/core/manual/selectDevicePriceHandle"
            raise e
        print(f"✅ 设备价格查询成功")




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

    instance = TestDevice()
    method = getattr(instance, "test_18_select_device_price")
    METHOD_RECORDED = False
    try:
        method()
        print("\n✅ " + "test_18_select_device_price" + " 执行通过")
    except Exception as e:
        exc_response = getattr(e, 'response', None)
        api_path_val = getattr(e, 'api_path', '') or base_tester.CURRENT_API_PATH or ""
        base_tester.record_result(
            "test_18_select_device_price",
            api_path_val,
            exc_response if exc_response else {"success": False, "message": str(e)},
            "FAILED", group=TEST_GROUP)
        print("\n❌ " + "test_18_select_device_price" + " 执行失败: " + str(e))

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
