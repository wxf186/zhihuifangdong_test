#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
智慧房东 APP - /core/houseAdd/cotenancyAdd 接口测试
"""

import sys
import os
sys.path.insert(0, os.path.normpath(os.path.join(os.path.dirname(__file__), '..')))

from base_tester import *

TEST_GROUP = "fy"
class TestHouseAdd:
    """/core/houseAdd/cotenancyAdd"""

    def test_06_cotenancy_add(self):
        """新增合租房源"""
        print("\n📋 测试新增合租房源...")
        response = api_request(
            "POST",
            "/core/houseAdd/cotenancyAdd",
            json_data={
                "provinceId": 19,
                "cityId": 561,
                "cityName": "杭州市",
                "communityId": 395875,
                "communityName": "合嵣悦府东区",
                "block": "9幢",
                "unit": "1单元",
                "name": "101室",
                "area": 87,
                "rent": 301,
                "cameraVoList": [],
                "newPvCost": True
            }
        )
        print(f"响应: {json.dumps(response, ensure_ascii=False, indent=2)}")
        validate_response(response)
        cotenancy_id = response.get("data")
        print(f"✅ 新增合租房源成功，合租房ID: {cotenancy_id}")
        record_result("test_06_cotenancy_add", "/core/houseAdd/cotenancyAdd", response, "PASSED", group=TEST_GROUP)



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

    instance = TestHouseAdd()
    method = getattr(instance, "test_06_cotenancy_add")
    METHOD_RECORDED = False
    try:
        method()
        print("\n✅ " + "test_06_cotenancy_add" + " 执行通过")
    except Exception as e:
        exc_response = getattr(e, 'response', None)
        api_path_val = getattr(e, 'api_path', '') or CURRENT_API_PATH or ""
        record_result(
            "test_06_cotenancy_add",
            api_path_val,
            exc_response if exc_response else {"success": False, "message": str(e)},
            "FAILED", group=TEST_GROUP)
        print("\n❌ " + "test_06_cotenancy_add" + " 执行失败: " + str(e))

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

