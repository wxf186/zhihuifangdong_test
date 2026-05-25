#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
智慧房东 APP - /core/app/contractExt/myContractNum 接口测试
"""

import sys
import os
sys.path.insert(0, os.path.normpath(os.path.join(os.path.dirname(__file__), '..')))

import base_tester

TEST_GROUP = "sy"

class TestContract:
    """/core/app/contractExt/myContractNum"""

    def test_15_my_contract_num(self):
        """我的合同数量"""
        print("\n📑 测试我的合同数量...")
        response = base_tester.api_request("GET", "/core/app/contractExt/myContractNum")
        print(f"响应: {base_tester.json.dumps(response, ensure_ascii=False, indent=2)}")
        base_tester.validate_response(response)
        print("✅ 合同数量获取成功")
        base_tester.record_result("test_15_my_contract_num", "/core/app/contractExt/myContractNum", response, "PASSED", group=TEST_GROUP)



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

    instance = TestContract()
    method = getattr(instance, "test_15_my_contract_num")
    METHOD_RECORDED = False
    try:
        method()
        print("\n✅ " + "test_15_my_contract_num" + " 执行通过")
    except Exception as e:
        exc_response = getattr(e, 'response', None)
        api_path_val = getattr(e, 'api_path', '') or base_tester.CURRENT_API_PATH or ""
        base_tester.record_result(
            "test_15_my_contract_num",
            api_path_val,
            exc_response if exc_response else {"success": False, "message": str(e)},
            "FAILED"
        , group=TEST_GROUP)
        print("\n❌ " + "test_15_my_contract_num" + " 执行失败: " + str(e))

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

