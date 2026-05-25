#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
智慧房东 APP - /core/houseAdd/cotenancyHouseEdit 接口测试
"""

import sys
import os
sys.path.insert(0, os.path.normpath(os.path.join(os.path.dirname(__file__), '..')))

import base_tester

TEST_GROUP = "fy"
class TestHouseAdd:
    """/core/houseAdd/cotenancyHouseEdit"""

    def test_07_cotenancy_house_edit(self):
        """合租房分间编辑"""
        print("\n📋 测试合租房分间编辑...")
        response = base_tester.api_request(
            "POST",
            "/core/houseAdd/cotenancyHouseEdit",
            json_data={
                "parentId": 1558024,
                "house": [
                    {"houseId": 0, "name": "1室", "rent": "333",
                     "houseStatus": {"name": "WAITING_RENT"},
                     "isEdit": True, "add": True,
                     "meterArr": [], "doorLockArr": [], "waterArr": [],
                     "meterAllocationProportion": 1, "waterAllocationProportion": 1,
                     "meterAddForms": [], "waterAddForms": []},
                    {"houseId": 0, "name": "2室", "rent": "444",
                     "houseStatus": {"name": "WAITING_RENT"},
                     "isEdit": True, "add": True,
                     "meterArr": [], "doorLockArr": [], "waterArr": [],
                     "meterAllocationProportion": 1, "waterAllocationProportion": 1,
                     "meterAddForms": [], "waterAddForms": []}
                ],
                "kitchenNumber": 1,
                "livingRoomNumber": 1,
                "roomNumber": 2,
                "toiletNumber": 1,
                "payMethod": "MONTH_PAY",
                "pledgeCount": 1,
                "perMonth": 1
            }
        )
        print(f"响应: {base_tester.json.dumps(response, ensure_ascii=False, indent=2)}")
        status = "PASSED" if response.get("success") else "FAILED"
        base_tester.record_result("test_07_cotenancy_house_edit", "/core/houseAdd/cotenancyHouseEdit", response, status, group=TEST_GROUP)
        if not response.get("success"):
            e = AssertionError(f"业务失败: {response.get('message', '未知错误')}")
            e.response = response
            e.api_path = "/core/houseAdd/cotenancyHouseEdit"
            raise e
        print(f"✅ 合租房分间编辑成功")




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

    instance = TestHouseAdd()
    method = getattr(instance, "test_07_cotenancy_house_edit")
    METHOD_RECORDED = False
    try:
        method()
        print("\n✅ " + "test_07_cotenancy_house_edit" + " 执行通过")
    except Exception as e:
        exc_response = getattr(e, 'response', None)
        api_path_val = getattr(e, 'api_path', '') or base_tester.CURRENT_API_PATH or ""
        base_tester.record_result(
            "test_07_cotenancy_house_edit",
            api_path_val,
            exc_response if exc_response else {"success": False, "message": str(e)},
            "FAILED", group=TEST_GROUP)
        print("\n❌ " + "test_07_cotenancy_house_edit" + " 执行失败: " + str(e))

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
