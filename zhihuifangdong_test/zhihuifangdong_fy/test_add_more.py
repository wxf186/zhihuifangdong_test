#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
智慧房东 APP - /core/web/apartment/addMore 接口测试
"""

import sys
import os
sys.path.insert(0, os.path.normpath(os.path.join(os.path.dirname(__file__), '..')))

import base_tester

TEST_GROUP = "fy"
class TestApartment:
    """/core/web/apartment/addMore"""

    def test_20_add_more(self):
        """批量添加公寓"""
        print("\n📋 测试批量添加公寓...")
        response = base_tester.api_request(
            "POST",
            "/core/web/apartment/addMore",
            json_data={
                "provinceId": "1",
                "provinceName": "上海市",
                "cityId": "6758",
                "cityName": "奉贤区",
                "communityId": "3672",
                "communityName": "新北路96弄小区",
                "block": "1幢",
                "unit": "1单元",
                "elevator": True,
                "totalFloor": 3,
                "managementList": [
                    {
                        "floor": 1,
                        "select": True,
                        "edit": False,
                        "num": 4,
                        "sum": [
                            {"value": 1, "label": False},
                            {"value": 2, "label": False},
                            {"value": 3, "label": False},
                            {"value": 4, "label": False}
                        ],
                        "list": [
                            {"name": "A1001", "templateId": 10388, "templateName": "佣金30模版-副本"},
                            {"name": "A1002", "templateId": 10388, "templateName": "佣金30模版-副本"},
                            {"name": "A1003", "templateId": 10388, "templateName": "佣金30模版-副本"},
                            {"name": "A1004", "templateId": 10388, "templateName": "佣金30模版-副本"}
                        ]
                    }
                ]
            }
        )
        print(f"响应: {base_tester.json.dumps(response, ensure_ascii=False, indent=2)}")
        base_tester.validate_response(response, allow_success_false=True)
        print(f"✅ 批量添加公寓成功")
        base_tester.record_result("test_20_add_more", "/core/web/apartment/addMore", response, "PASSED", group=TEST_GROUP)



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

    instance = TestApartment()
    method = getattr(instance, "test_20_add_more")
    METHOD_RECORDED = False
    try:
        method()
        print("\n✅ " + "test_20_add_more" + " 执行通过")
    except Exception as e:
        exc_response = getattr(e, 'response', None)
        api_path_val = getattr(e, 'api_path', '') or base_tester.CURRENT_API_PATH or ""
        base_tester.record_result(
            "test_20_add_more",
            api_path_val,
            exc_response if exc_response else {"success": False, "message": str(e)},
            "FAILED", group=TEST_GROUP)
        print("\n❌ " + "test_20_add_more" + " 执行失败: " + str(e))

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

