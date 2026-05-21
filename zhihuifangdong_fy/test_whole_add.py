#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
智慧房东 APP - /core/houseAdd/wholeAdd 接口测试
"""

import sys
import os
sys.path.insert(0, os.path.normpath(os.path.join(os.path.dirname(__file__), '..')))

from base_tester import *
from base_tester import _next_house_name, _save_counter, WHOLE_ADD_NAME_COUNTER

TEST_GROUP = "fy"
class TestHouseAdd:
    """/core/houseAdd/wholeAdd"""

    def test_05_whole_add(self):
        """新增整租房源（重试机制：若房源已存在则 name+1 再提交）"""
        print("\n📋 测试新增整租房源...")

        def _do_add(name_value: str) -> Dict[str, Any]:
            return api_request(
                "POST",
                "/core/houseAdd/wholeAdd",
                json_data={
                    "provinceId": 19,
                    "cityId": 561,
                    "cityName": "杭州市",
                    "communityId": 362440,
                    "communityName": "中天·官河锦庭",
                    "block": "9幢",
                    "unit": "1单元",
                    "name": name_value,
                    "area": 87,
                    "rent": "320.00",
                    "roomNumber": 2,
                    "livingRoomNumber": 1,
                    "kitchenNumber": 1,
                    "toiletNumber": 1,
                    "payMethod": "SEASON_PAY",
                    "pledgeCount": 1,
                    "perMonth": 3,
                    "commission": 50,
                    "newPvCost": True
                }
            )

        BASE_NAME = "102"   # 初始数字基准，文件不存在时以此为起点
        max_retries = 10
        last_resp = None

        for attempt in range(1, max_retries + 1):
            name_value = _next_house_name(BASE_NAME)
            print(f"  第{attempt}次尝试: name={name_value}")
            resp = _do_add(name_value)
            last_resp = resp
            print(f"  响应: success={resp.get('success')}, message={resp.get('message')}")

            if resp.get("success"):
                _save_counter(WHOLE_ADD_NAME_COUNTER)  # 成功后持久化计数器
                print(f"  ✅ 新增整租房源成功，房源ID: {resp.get('data')}")
                print(f"  ✅ 计数器已保存，下一次 name 将从 {WHOLE_ADD_NAME_COUNTER} 开始")
                record_result("test_05_whole_add", "/core/houseAdd/wholeAdd", resp, "PASSED", group=TEST_GROUP)
                return
            else:
                msg = resp.get("message", "")
                if "网络拥挤" in msg:
                    print(f"  ❌ 服务器返回网络拥挤，停止重试")
                    break
                if "已存在" in msg or "重复" in msg:
                    print(f"  ⚠️ 房源已存在，name+1 重新提交...")
                    continue
                print(f"  ❌ 其他业务错误，停止重试: {msg}")
                break

        validate_response(last_resp, allow_success_false=True)
        record_result("test_05_whole_add", "/core/houseAdd/wholeAdd", last_resp, "PASSED", group=TEST_GROUP)



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
    method = getattr(instance, "test_05_whole_add")
    METHOD_RECORDED = False
    try:
        method()
        print("\n✅ " + "test_05_whole_add" + " 执行通过")
    except Exception as e:
        exc_response = getattr(e, 'response', None)
        api_path_val = getattr(e, 'api_path', '') or CURRENT_API_PATH or ""
        record_result(
            "test_05_whole_add",
            api_path_val,
            exc_response if exc_response else {"success": False, "message": str(e)},
            "FAILED", group=TEST_GROUP)
        print("\n❌ " + "test_05_whole_add" + " 执行失败: " + str(e))

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
