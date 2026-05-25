#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
智慧房东 APP - /core/houseAdd/cotenancyAdd 接口测试
"""

import sys
import os
import re
sys.path.insert(0, os.path.normpath(os.path.join(os.path.dirname(__file__), '..')))

import base_tester

TEST_GROUP = "fy"

def extract_room_number(name):
    """从房间名提取数字部分，如 '101室' -> 101"""
    m = re.search(r'(\d+)室', name)
    return int(m.group(1)) if m else None

def build_room_name(name, new_number):
    """替换房间号，如 '101室' + 1 -> '102室'"""
    return re.sub(r'\d+室', f'{new_number}室', name)

class TestHouseAdd:
    """/core/houseAdd/cotenancyAdd"""

    def test_06_cotenancy_add(self):
        """新增合租房源"""
        print("\n📋 测试新增合租房源...")

        base_data = {
            "provinceId": 19,
            "cityId": 561,
            "cityName": "杭州市",
            "communityId": 378773,
            "communityName": "中天·官河锦庭",
            "block": "11幢",
            "unit": "11单元",
            "name": "1101室",
            "area": 123,
            "rent": 356,
            "cameraVoList": [],
            "newPvCost": True
        }

        max_retries = 3
        response = None
        for attempt in range(max_retries):
            print(f"\n--- 第 {attempt + 1} 次提交 ---")
            print(f"房间名: {base_data['name']}")
            response = base_tester.api_request(
                "POST",
                "/core/houseAdd/cotenancyAdd",
                json_data=base_data.copy()
            )
            print(f"响应: {base_tester.json.dumps(response, ensure_ascii=False, indent=2)}")

            if response.get("success"):
                cotenancy_id = response.get("data")
                print(f"✅ 新增合租房源成功，合租房ID: {cotenancy_id}")
                base_tester.record_result("test_06_cotenancy_add", "/core/houseAdd/cotenancyAdd", response, "PASSED", group=TEST_GROUP)
                return

            msg = response.get("message", "")
            code = response.get("code", "")

            # 仅房源已存在时重试
            if code == "A0076" or "已有" in msg or "已存在" in msg:
                room_num = extract_room_number(base_data["name"])
                if room_num is not None:
                    new_num = room_num + 1
                    base_data["name"] = build_room_name(base_data["name"], new_num)
                    print(f"⚠️ 房源已存在，房间号+1 -> {base_data['name']}，准备重试...")
                    continue

            # 其他错误直接失败
            base_tester.record_result("test_06_cotenancy_add", "/core/houseAdd/cotenancyAdd", response, "FAILED", group=TEST_GROUP)
            base_tester.validate_response(response)
            return

        # 3次均失败
        print(f"\n❌ 提交 {max_retries} 次均失败: 房源持续冲突")
        base_tester.record_result("test_06_cotenancy_add", "/core/houseAdd/cotenancyAdd", response, "FAILED", group=TEST_GROUP)
        raise Exception(f"重试 {max_retries} 次后仍失败: {response.get('message')}")



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

    from config.token_manager import get_or_login_token
    token_info = get_or_login_token(api_config.ACTIVE_ENV)
    base_tester.set_token(token_info["token"])

    instance = TestHouseAdd()
    method = getattr(instance, "test_06_cotenancy_add")
    METHOD_RECORDED = False
    try:
        method()
        print("\n✅ " + "test_06_cotenancy_add" + " 执行通过")
    except Exception as e:
        exc_response = getattr(e, 'response', None)
        api_path_val = getattr(e, 'api_path', '') or base_tester.CURRENT_API_PATH or ""
        base_tester.record_result(
            "test_06_cotenancy_add",
            api_path_val,
            exc_response if exc_response else {"success": False, "message": str(e)},
            "FAILED", group=TEST_GROUP)
        print("\n❌ " + "test_06_cotenancy_add" + " 执行失败: " + str(e))

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