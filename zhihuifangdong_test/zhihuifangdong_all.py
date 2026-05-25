#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
智慧房东APP - 合并测试报告生成器
串行执行 sy.py 和 fy.py，合并结果生成统一 HTML 报告

用法:
    python zhihuifangdong_all.py [--env formal]
"""

import sys
import os
import json
import subprocess
from datetime import datetime
import shutil

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
TEST_DIR = SCRIPT_DIR  # zhihuifangdong_test/
REPORTS_DIR = os.path.join(SCRIPT_DIR, "reports")  # zhihuifangdong_test/reports/
sy_script = os.path.join(SCRIPT_DIR, "zhihuifangdong_sy", "zhihuifangdong_sy.py")
fy_script = os.path.join(SCRIPT_DIR, "zhihuifangdong_fy", "zhihuifangdong_fy.py")
sy_json = os.path.join(SCRIPT_DIR, "zhihuifangdong_sy", "_sy_results.json")
fy_json = os.path.join(SCRIPT_DIR, "zhihuifangdong_fy", "_fy_results.json")


def patch_script_add_output_json_arg(script_path: str):
    """给脚本 __main__ 添加 --output-json 参数支持"""
    with open(script_path, encoding="utf-8") as f:
        lines = f.readlines()

    # 找 __main__ 块的开始行（593 左右）
    in_main = False
    main_start = -1
    for i, line in enumerate(lines):
        if line.startswith("if __name__") and "__main__" in line:
            in_main = True
            main_start = i
            break

    if main_start < 0:
        print(f"  ⚠️ 未找到 __main__ 块，跳过 {script_path}")
        return False

    # 检查是否已有 --output-json 逻辑
    content = "".join(lines)
    if "--output-json" in content:
        return True  # 已有

    # 在 parser.add_argument 之后插入 --output-json 参数
    arg_insert_line = -1
    for i in range(main_start, len(lines)):
        if "parser.add_argument" in lines[i] and "add_argument" not in lines[i - 1]:
            arg_insert_line = i
        # 找到 parser.parse_args() 所在行
        if "parser.parse_args()" in lines[i]:
            break

    if arg_insert_line < 0:
        print(f"  ⚠️ 未找到 argparse 位置，跳过 {script_path}")
        return False

    # 在 parser.parse_args() 前插入新参数
    indent = "    "
    new_arg = f'{indent}parser.add_argument("--output-json", action="store_true", help="仅输出JSON不生成报告")\n'

    # 找 parse_args 行的索引
    parse_args_line = -1
    for i in range(main_start, len(lines)):
        if "parser.parse_args()" in lines[i]:
            parse_args_line = i
            break

    lines.insert(parse_args_line, new_arg)

    # 在 generate_html_report 调用前插入 JSON 输出逻辑
    # 找到 generate_html_report 所在行
    for i in range(main_start, len(lines)):
        if "generate_html_report(TEST_RESULTS" in lines[i]:
            # 在它前面插入条件判断和 JSON 输出
            output_block = f'''    if args.output_json:
        json_path = os.path.join(os.path.dirname(__file__), "_sy_results.json" if "sy" in __file__ else "_fy_results.json")
        with open(json_path, "w", encoding="utf-8") as _f:
            json.dump(TEST_RESULTS, _f, ensure_ascii=False, indent=2)
        print(f"📄 JSON已保存: {{json_path}}")
        sys.exit(0)

'''
            lines.insert(i, output_block)
            break

    with open(script_path, "w", encoding="utf-8") as f:
        f.writelines(lines)

    return True


def run_script(script_path: str, output_json: str, env_args: list) -> list:
    """运行脚本（带 --output-json），返回 TEST_RESULTS 列表"""
    cmd = [sys.executable, script_path, "--output-json"] + env_args

    print(f"\n{'=' * 60}")
    print(f"▶ {' '.join(cmd)}")
    print(f"{'=' * 60}")

    result = subprocess.run(cmd, capture_output=True, text=True, cwd=TEST_DIR)
    # 打印最后 2000 字符
    out = result.stdout
    print(out[-2000:] if len(out) > 2000 else out)
    if result.stderr:
        print(f"[stderr]: {result.stderr[-500:]}")

    if os.path.exists(output_json):
        with open(output_json, encoding="utf-8") as f:
            return json.load(f)
    print(f"  ⚠️ 未找到输出文件: {output_json}")
    return []


def main():
    import argparse
    parser = argparse.ArgumentParser(description="智慧房东APP合并测试")
    parser.add_argument("--env", default="test2", choices=["test2", "formal"],
                        help="运行环境: test2 (默认) 或 formal")
    args = parser.parse_args()

    env_args = []
    if args.env != "test2":
        env_args = ["--env", args.env]

    START_TIME = datetime.now()

    # ---- 一次性给两个脚本打补丁（添加 --output-json 支持）----
    print("检查脚本是否支持 --output-json 参数...")
    patch_script_add_output_json_arg(sy_script)
    patch_script_add_output_json_arg(fy_script)

    # ---- 清理旧的 JSON 文件 ----
    for f in [sy_json, fy_json]:
        if os.path.exists(f):
            os.remove(f)

    # ---- 串行运行两个脚本 ----
    sy_results = run_script(sy_script, sy_json, env_args)
    print(f"\nsy.py 返回 {len(sy_results)} 条结果")

    fy_results = run_script(fy_script, fy_json, env_args)
    print(f"\nfy.py 返回 {len(fy_results)} 条结果")

    # ---- 合并 ----
    all_results = sy_results + fy_results
    if not all_results:
        print("❌ 未获取到任何测试结果，请检查脚本是否正常运行")
        return

    passed = sum(1 for r in all_results if r["status"] == "PASSED")
    failed = sum(1 for r in all_results if r["status"] == "FAILED")
    total = len(all_results)
    pass_rate = f"{(passed / total * 100):.1f}%" if total > 0 else "0%"

    print(f"\n{'=' * 60}")
    print(f"📊 合并结果: {total} 个接口 | {passed} 通过 | {failed} 失败 | 通过率 {pass_rate}")
    print(f"{'=' * 60}")

    END_TIME = datetime.now()
    # ---- 生成统一 HTML 报告 ----
    sys.path.insert(0, PROJECT_DIR)
    from config.report_generator import generate_report
    os.makedirs(REPORTS_DIR, exist_ok=True)
    date_str = datetime.now().strftime("%Y-%m-%d_%H%M")
    report_path = os.path.join(REPORTS_DIR, f"all-{date_str}.html")
    generate_report(
        all_results,
        output_path=report_path,
        start_time=START_TIME.strftime("%Y-%m-%d %H:%M:%S"),
        end_time=END_TIME.strftime("%Y-%m-%d %H:%M:%S"),
    )
    print(f"\n✅ HTML报告已生成: {report_path}")
    print(f"   打开方式: file://{os.path.abspath(report_path)}")


if __name__ == "__main__":
    main()
