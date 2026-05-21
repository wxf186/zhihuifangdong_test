#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
智慧房东 APP - /core/app/activity/platformPic 接口测试
"""

import sys
import os
sys.path.insert(0, os.path.normpath(os.path.join(os.path.dirname(__file__), '..')))

from base_tester import *

TEST_GROUP = "sy"

class TestActivity:
    """/core/app/activity/platformPic"""

    def test_21_platform_pic(self):
        """平台图片"""
        print("\n🎨 测试平台图片...")
        response = api_request("GET", "/core/app/activity/platformPic")
        print(f"响应: {json.dumps(response, ensure_ascii=False, indent=2)}")
        validate_response(response)
        print("✅ 平台图片获取成功")
        record_result("test_21_platform_pic", "/core/app/activity/platformPic", response, "PASSED", group=TEST_GROUP)



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
    set_token(token_info["token"])

    instance = TestActivity()
    method = getattr(instance, "test_21_platform_pic")
    METHOD_RECORDED = False
    try:
        method()
        print("\n✅ " + "test_21_platform_pic" + " 执行通过")
    except Exception as e:
        exc_response = getattr(e, 'response', None)
        api_path_val = getattr(e, 'api_path', '') or CURRENT_API_PATH or ""
        record_result(
            "test_21_platform_pic",
            api_path_val,
            exc_response if exc_response else {"success": False, "message": str(e)},
            "FAILED"
        , group=TEST_GROUP)
        print("\n❌ " + "test_21_platform_pic" + " 执行失败: " + str(e))

    if args.output_json:
        json_path = os.path.join(os.path.dirname(__file__), "_results.json")
        with open(json_path, "w", encoding="utf-8") as _f:
            json.dump(TEST_RESULTS, _f, ensure_ascii=False, indent=2)
        print("📄 JSON已保存: " + json_path)
    else:
        config_dir = os.path.join(os.path.dirname(__file__), '..', 'config')
        report_path = os.path.join(config_dir, "report.html")
        generate_html_report(TEST_RESULTS, output_path=report_path)
        print("\n✅ 报告已生成: " + report_path)

