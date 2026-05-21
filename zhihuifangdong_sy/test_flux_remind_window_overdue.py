#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
智慧房东 APP - /netty/web/meter/fluxRemindWindowOverdue 接口测试
"""

import sys
import os
import time
sys.path.insert(0, os.path.normpath(os.path.join(os.path.dirname(__file__), '..')))

from base_tester import *

TEST_GROUP = "sy"

class TestMeter:
    """/netty/web/meter/fluxRemindWindowOverdue"""

    def test_26_flux_remind_window_overdue(self):
        """流量欠费提醒"""
        print("\n📡 测试流量欠费提醒...")
        _start = time.time()
        time.sleep(0.5)
        response = api_request("GET", "/netty/web/meter/fluxRemindWindowOverdue",
                               params={"userId": USER_ID},
                               timeout=60)
        print(f"响应: {json.dumps(response, ensure_ascii=False, indent=2)}")
        try:
            validate_response(response)
            record_result("test_26_flux_remind_window_overdue", "/netty/web/meter/fluxRemindWindowOverdue", response, "PASSED", group=TEST_GROUP)
        except AssertionError:
            record_result("test_26_flux_remind_window_overdue", "/netty/web/meter/fluxRemindWindowOverdue", response, "FAILED", group=TEST_GROUP)
            raise
        finally:
            if TEST_RESULTS:
                TEST_RESULTS[-1]["duration"] = int((time.time() - _start) * 1000)
        print("✅ 流量欠费提醒查询完成")



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

    instance = TestMeter()
    method = getattr(instance, "test_26_flux_remind_window_overdue")
    METHOD_RECORDED[0]["flag"] = False
    try:
        method()
        print("\n✅ " + "test_26_flux_remind_window_overdue" + " 执行通过")
    except Exception as e:
        print("\n❌ " + "test_26_flux_remind_window_overdue" + " 执行失败: " + str(e))

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

