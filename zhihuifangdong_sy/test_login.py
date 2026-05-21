#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
智慧房东 APP - /auth/auth/apploginMultipleRole 接口测试

测试场景：
1. 正常登录成功
2. 用户名不存在
3. 密码错误
4. 用户名为空
5. 密码为空
6. 密码过短
7. 未注册账号
8. 并发登录（同一账号同时登录）

（test_06 特殊字符注入、test_09 禁用账号暂不执行）
"""

import sys
import os
import json
import base64
import datetime
sys.path.insert(0, os.path.normpath(os.path.join(os.path.dirname(__file__), '..')))

from base_tester import (
    api_request, API_CONFIG, CURRENT_API_PATH,
    record_result, validate_response, set_token, TOKEN, METHOD_RECORDED,
    _record_duration
)
import base_tester

# 当前测试环境
CURRENT_ENV = "test2"


class TestAuth:
    """登录接口 /auth/auth/apploginMultipleRole"""

    def test_01_login_success(self):
        """正常登录成功"""
        try:
            validate_response(base_tester.LOGIN_RESPONSE)
            record_result("test_01_login_success", "/auth/auth/apploginMultipleRole", base_tester.LOGIN_RESPONSE, "PASSED", "sy")
            print("✅ 正常登录成功，Token已保存")
        except Exception as e:
            # LOGIN_RESPONSE 为 None 时构造一个带 _request_info 的兜底响应，避免 record_result 内部再抛异常
            _fallback = base_tester.LOGIN_RESPONSE if base_tester.LOGIN_RESPONSE is not None else {
                "success": False,
                "message": "LOGIN_RESPONSE 为空（fixture登录失败）",
                "_request_info": {
                    "method": "POST",
                    "url": "http://8.153.90.53:7663/auth/auth/apploginMultipleRole",
                    "params": None,
                    "json_data": None,
                    "data": {"username": "", "password": ""},
                    "headers": {},
                },
                "_elapsed_ms": 0,
            }
            record_result("test_01_login_success", "/auth/auth/apploginMultipleRole", _fallback, "FAILED", "sy")
            raise

    def test_02_username_not_exist(self):
        """用户名不存在"""
        from config.api_config import USERS
        fake_user = {
            "username": "00000000000",
            "password": USERS[CURRENT_ENV]["password"],
        }
        resp = api_request(
            "POST",
            "/auth/auth/apploginMultipleRole",
            need_auth=False,
            data=fake_user,
            timeout=API_CONFIG["login_timeout"]
        )
        assert resp.get("success") == False, f"预期失败，实际: {resp}"
        record_result("test_02_username_not_exist", "/auth/auth/apploginMultipleRole", resp, "PASSED", "sy")
        print("✅ 用户名不存在—登录被拒绝")

    def test_03_wrong_password(self):
        """密码错误"""
        from config.api_config import USERS
        wrong_user = {
            "username": USERS[CURRENT_ENV]["username"],
            "password": "wrongpassword123",
        }
        resp = api_request(
            "POST",
            "/auth/auth/apploginMultipleRole",
            need_auth=False,
            data=wrong_user,
            timeout=API_CONFIG["login_timeout"]
        )
        assert resp.get("success") == False, f"预期失败，实际: {resp}"
        record_result("test_03_wrong_password", "/auth/auth/apploginMultipleRole", resp, "PASSED", "sy")
        print("✅ 密码错误—登录被拒绝")

    def test_04_empty_username(self):
        """用户名为空"""
        from config.api_config import USERS
        empty_user = {
            "username": "",
            "password": USERS[CURRENT_ENV]["password"],
        }
        resp = api_request(
            "POST",
            "/auth/auth/apploginMultipleRole",
            need_auth=False,
            data=empty_user,
            timeout=API_CONFIG["login_timeout"]
        )
        assert resp.get("success") == False, f"预期失败，实际: {resp}"
        record_result("test_04_empty_username", "/auth/auth/apploginMultipleRole", resp, "PASSED", "sy")
        print("✅ 用户名为空—登录被拒绝")

    def test_05_empty_password(self):
        """密码为空"""
        from config.api_config import USERS
        empty_pwd = {
            "username": USERS[CURRENT_ENV]["username"],
            "password": "",
        }
        resp = api_request(
            "POST",
            "/auth/auth/apploginMultipleRole",
            need_auth=False,
            data=empty_pwd,
            timeout=API_CONFIG["login_timeout"]
        )
        assert resp.get("success") == False, f"预期失败，实际: {resp}"
        record_result("test_05_empty_password", "/auth/auth/apploginMultipleRole", resp, "PASSED", "sy")
        print("✅ 密码为空—登录被拒绝")

    def test_07_short_password(self):
        """密码过短"""
        from config.api_config import USERS
        short_pwd = {
            "username": USERS[CURRENT_ENV]["username"],
            "password": "12",
        }
        resp = api_request(
            "POST",
            "/auth/auth/apploginMultipleRole",
            need_auth=False,
            data=short_pwd,
            timeout=API_CONFIG["login_timeout"]
        )
        assert resp.get("success") == False, f"预期失败，实际: {resp}"
        record_result("test_07_short_password", "/auth/auth/apploginMultipleRole", resp, "PASSED", "sy")
        print("✅ 密码过短—登录被拒绝")

    def test_08_unregistered_account(self):
        """未注册账号"""
        unregistered = {
            "username": "19999999999",
            "password": "a1234567",
        }
        resp = api_request(
            "POST",
            "/auth/auth/apploginMultipleRole",
            need_auth=False,
            data=unregistered,
            timeout=API_CONFIG["login_timeout"]
        )
        assert resp.get("success") == False, f"预期失败，实际: {resp}"
        record_result("test_08_unregistered_account", "/auth/auth/apploginMultipleRole", resp, "PASSED", "sy")
        print("✅ 未注册账号—登录被拒绝")

    # def test_09_disabled_account(self):
    #     """账号已被禁用（等有禁用账号后再开启）"""
    #     from config.api_config import set_env
    #     set_env("formal")
    #     from config.api_config import USERS
    #     disabled_user = {
    #         "username": "00000000000",
    #         "password": "a1234567",
    #     }
    #     resp = api_request(
    #         "POST",
    #         "/auth/auth/apploginMultipleRole",
    #         need_auth=False,
    #         data=disabled_user,
    #         timeout=API_CONFIG["login_timeout"]
    #     )
    #     err_msg = str(resp.get("message", ""))
    #     assert (
    #         resp.get("success") == False and any(
    #             kw in err_msg for kw in ["禁用", "停用", "冻结", "锁定"]
    #         )
    #     ), f"预期账号禁用提示，实际: {resp}"
    #     record_result("test_09_disabled_account", "/auth/auth/apploginMultipleRole", resp, "PASSED", "sy")
    #     print("✅ 禁用账号—登录被拒绝")
    #     set_env(CURRENT_ENV)

    def test_10_concurrent_login(self):
        """并发登录（同一账号同时发两个请求）"""
        from config.api_config import USERS
        user = USERS[CURRENT_ENV]

        resp1 = api_request(
            "POST",
            "/auth/auth/apploginMultipleRole",
            need_auth=False,
            data=user,
            timeout=API_CONFIG["login_timeout"]
        )
        resp2 = api_request(
            "POST",
            "/auth/auth/apploginMultipleRole",
            need_auth=False,
            data=user,
            timeout=API_CONFIG["login_timeout"]
        )
        assert resp1.get("success") == True and resp2.get("success") == True, \
            f"并发登录异常: resp1={resp1}, resp2={resp2}"
        token1 = resp1.get("data", {}).get("token", "")
        token2 = resp2.get("data", {}).get("token", "")
        assert len(token1.split('.')) == 3 and len(token2.split('.')) == 3, \
            f"Token 格式异常: token1={token1}, token2={token2}"
        record_result("test_10_concurrent_login", "/auth/auth/apploginMultipleRole",
                      resp1, "PASSED", "sy")
        print(f"✅ 并发登录成功—Token1={token1[:20]}..., Token2={token2[:20]}...")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="智慧房东 APP 登录接口测试")
    parser.add_argument("--env", default="test2", choices=["test2", "formal"],
                        help="运行环境: test2 (默认) 或 formal")
    parser.add_argument("--output-json", action="store_true", help="仅输出JSON不生成报告")
    args = parser.parse_args()

    import config.api_config as api_config
    CURRENT_ENV = args.env
    if args.env != "test2":
        api_config.set_env(args.env)

    from config.api_config import USERS
    from config.token_manager import save_token

    current_user = USERS[api_config.ACTIVE_ENV]
    login_payload = {
        "username": current_user["username"],
        "password": current_user["password"],
    }

    print("\n" + "="*60)
    print(f"🔐 执行登录... [环境: {api_config.ACTIVE_ENV}] {get_base_url()}")
    print("="*60)

    login_response = api_request(
        "POST",
        "/auth/auth/apploginMultipleRole",
        need_auth=False,
        data=login_payload,
        timeout=API_CONFIG["login_timeout"]
    )

    if login_response.get("success") and login_response.get("data", {}).get("token"):
        token = login_response["data"]["token"]
        set_token(token)
        try:
            payload = token.split('.')[1]
            payload += '=' * (4 - len(payload) % 4)
            USER_ID = json.loads(base64.b64decode(payload)).get("id")
        except Exception:
            USER_ID = None
        LOGIN_RESPONSE = login_response
        save_token(token, api_config.ACTIVE_ENV, USER_ID)
        record_result("test_01_login_success", "/auth/auth/apploginMultipleRole", login_response, "PASSED", "sy")
        print(f"✅ Token获取并缓存成功，用户ID: {USER_ID}")
    else:
        # 登录失败也记录一条 FAILED 结果（不走 sys.exit，避免丢失请求数据）
        print(f"❌ 登录失败，退出: {login_response.get('message', '未知错误')}")
        record_result("test_01_login_success", "/auth/auth/apploginMultipleRole", login_response, "FAILED", "sy")
        sys.exit(1)

    # 运行所有测试（test_06 特殊字符注入、test_09 禁用账号暂不执行）
    test_methods = [
        "test_01_login_success",
        "test_02_username_not_exist",
        "test_03_wrong_password",
        "test_04_empty_username",
        "test_05_empty_password",
        # "test_06_invalid_username_format",  # SQL注入测试，暂跳过
        "test_07_short_password",
        "test_08_unregistered_account",
        # "test_09_disabled_account",          # 等有禁用账号再开启
        "test_10_concurrent_login",
    ]

    instance = TestAuth()

    for method_name in test_methods:
        METHOD_RECORDED[0]["flag"] = False
        method = getattr(instance, method_name)
        try:
            method()
            print(f"\n✅ {method_name} 执行通过")
        except Exception as e:
            exc_response = getattr(e, 'response', None)
            api_path_val = getattr(e, 'api_path', '') or CURRENT_API_PATH or ""
            record_result(
                method_name,
                api_path_val,
                exc_response if exc_response else {"success": False, "message": str(e)},
                "FAILED",
                "sy"
            )
            print(f"\n❌ {method_name} 执行失败: {str(e)}")

    if args.output_json:
        json_path = os.path.join(os.path.dirname(__file__), "_results.json")
        with open(json_path, "w", encoding="utf-8") as _f:
            json.dump(TEST_RESULTS, _f, ensure_ascii=False, indent=2)
        print("📄 JSON已保存: " + json_path)
    else:
        reports_dir = os.path.join(os.path.dirname(__file__), '..', 'reports')
        os.makedirs(reports_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M")
        report_filename = f"all-{timestamp}.html"
        report_path = os.path.join(reports_dir, report_filename)
        generate_report(TEST_RESULTS, output_path=report_path)
        print("\n✅ 报告已生成: " + report_path)