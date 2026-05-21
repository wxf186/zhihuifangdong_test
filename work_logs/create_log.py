#!/usr/bin/env python3
"""每日工作日志创建脚本"""
import os
from datetime import date, datetime

work_logs_dir = os.path.dirname(os.path.abspath(__file__))
today = date.today().strftime("%Y-%m-%d")
log_file = os.path.join(work_logs_dir, f"{today}.md")
now = datetime.now().strftime("%H:%M")

if not os.path.exists(log_file):
    with open(log_file, "w", encoding="utf-8") as f:
        f.write(f"# {today} 工作日志\n")
    print(f"Created: {log_file}")
else:
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"\n---\n* {now } 自动归档\n")
    print(f"Appended: {log_file}")