#!/usr/bin/env python3
"""
定时同步脚本：扫描项目结构与配置文件，将变更内容追加到 NOTES.md。
同时读取当天 git commit 历史，作为工作内容追加到 create_log.py 的日志文件。
配合 cron 每天 20:20 执行。
"""
import subprocess
import os
import json
import hashlib
from datetime import datetime, date
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONFIG_DIR = PROJECT_ROOT / "config"
NOTES_FILE = PROJECT_ROOT / "NOTES.md"
SNAPSHOT_FILE = CONFIG_DIR / ".structure_snapshot.json"
WORK_LOGS_DIR = PROJECT_ROOT / "work_logs"

# 需要检测变更的关键文件/目录（相对于项目根）
WATCH_TARGETS = [
    "base_tester.py",
    "config/api_config.py",
    "config/report_generator.py",
    "config/token_manager.py",
    "config/sync_notes.py",
    "zhihuifangdong_all.py",
    "zhihuifangdong_fy",
    "zhihuifangdong_sy",
    "work_logs/create_log.py",
    "requirements.txt",
    "NOTES.md",
]

# 扫描时忽略的运行时产物
IGNORE_PATTERNS = ["_results.json", "__pycache__", ".pyc", ".pytest_cache"]


def get_file_hash(path: Path) -> str:
    """计算文件 MD5 哈希"""
    if not path.exists():
        return "FILE_NOT_EXIST"
    if path.is_dir():
        return "DIR"
    with open(path, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()


def scan_structure(root: Path) -> dict:
    """扫描项目结构，返回 {rel_path: hash}"""
    result = {}
    for target in WATCH_TARGETS:
        full_path = root / target
        if full_path.exists():
            if full_path.is_dir():
                # 目录：列出所有文件（不含 __pycache__）
                for f in full_path.rglob("*"):
                    if any(p in f.parts for p in ["__pycache__", ".pytest_cache"]) or \
                       any(f.name.endswith(p) for p in [".pyc", "_results.json"]):
                        continue
                    rel = f.relative_to(root)
                    result[str(rel)] = get_file_hash(f)
            else:
                result[target] = get_file_hash(full_path)
    return result


def load_snapshot() -> dict:
    """加载上次快照"""
    if SNAPSHOT_FILE.exists():
        with open(SNAPSHOT_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"structure": {}, "timestamp": None}


def save_snapshot(structure: dict):
    """保存当前快照"""
    with open(SNAPSHOT_FILE, "w", encoding="utf-8") as f:
        json.dump({"structure": structure, "timestamp": datetime.now().isoformat()}, f, ensure_ascii=False, indent=2)


def detect_changes(old: dict, new: dict) -> list:
    """对比新旧快照，返回变更列表"""
    changes = []
    all_keys = set(old.keys()) | set(new.keys())
    for key in sorted(all_keys):
        old_hash = old.get(key)
        new_hash = new.get(key)
        if old_hash != new_hash:
            if old_hash == "FILE_NOT_EXIST":
                changes.append(f"  + 新增: `{key}`")
            elif new_hash == "FILE_NOT_EXIST":
                changes.append(f"  - 删除: `{key}`")
            else:
                # 内容变更，区分文件还是目录
                if old_hash == "DIR" or new_hash == "DIR":
                    changes.append(f"  ~ 目录变更: `{key}`")
                else:
                    changes.append(f"  ~ 修改: `{key}`")
    return changes


def generate_changelog(changes: list, timestamp: str) -> str:
    """生成变更记录"""
    today = date.today().strftime("%Y-%m-%d")
    lines = [
        f"\n### {today} 项目变更\n",
        f"_自动扫描于 {timestamp}_\n",
    ]
    if changes:
        lines.append("\n".join(changes))
    else:
        lines.append("\n无变更。\n")
    return "\n".join(lines)


def append_to_notes(changelog: str):
    """追加变更记录到 NOTES.md 末尾"""
    with open(NOTES_FILE, "a", encoding="utf-8") as f:
        f.write(changelog + "\n")


def append_to_worklog(changes: list, timestamp: str):
    """追加到当日工作日志（create_log.py 的文件）"""
    today = date.today().strftime("%Y-%m-%d")
    log_file = WORK_LOGS_DIR / f"{today}.md"

    lines = []
    # 文件变更（每个文件附加当天所有 commit message）
    if changes:
        lines.append("\n文件变更:")
        for change in changes:
            lines.append(describe_change(change))
    else:
        lines.append("\n文件变更:\n  无变更。")

    # 今日工作（git commit）
    commits = get_git_commits_today()
    if commits:
        lines.append("\n今日工作:")
        for commit in commits:
            lines.append(f"  - {commit}")
    else:
        lines.append("\n今日工作:\n  无 commit 记录（请确认今日工作已提交）")

    content = "\n".join(lines) + "\n"
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(content)


def get_git_commits_today() -> list:
    """读取当天所有 git commit（按时间倒序）"""
    today = date.today().strftime("%Y-%m-%d")
    try:
        result = subprocess.run(
            ["git", "log", "--since=" + today + " 00:00", "--until=" + today + " 23:59",
             "--pretty=format:%h %s", "--reverse"],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
        )
        if result.returncode == 0 and result.stdout.strip():
            return [line.strip() for line in result.stdout.strip().split("\n") if line.strip()]
    except Exception as e:
        print(f"[sync_notes] git log 读取失败: {e}")
    return []


def get_file_commits_today(file_path: str) -> list:
    """读取指定文件当天的所有 commit message"""
    today = date.today().strftime("%Y-%m-%d")
    try:
        result = subprocess.run(
            ["git", "log", "--since=" + today + " 00:00", "--until=" + today + " 23:59",
             "--pretty=format:%h %s", "--reverse", "--", file_path],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
        )
        if result.returncode == 0 and result.stdout.strip():
            return [line.strip() for line in result.stdout.strip().split("\n") if line.strip()]
    except Exception:
        pass
    return []


def describe_change(change_line: str) -> str:
    """
    将变更行转为详细描述，附加当天 commit message。
    change_line 格式如: "  ~ 修改: `base_tester.py`"
    返回带 commit 详情的多行字符串。
    """
    # 解析出文件路径（去掉缩进和反引号）
    parts = change_line.strip().split("`")
    if len(parts) < 2:
        return change_line
    file_path = parts[1]

    commits = get_file_commits_today(file_path)
    if commits:
        lines = [change_line]
        for commit in commits:
            lines.append(f"    → {commit}")
        return "\n".join(lines)
    else:
        # 无 commit 说明（未提交或新增文件）
        return change_line + "\n    → （未提交或无变更记录）"


def main():
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    print(f"[sync_notes] 开始扫描... {now}")

    new_structure = scan_structure(PROJECT_ROOT)
    old_snapshot = load_snapshot()
    old_structure = old_snapshot.get("structure", {})

    changes = detect_changes(old_structure, new_structure)
    changelog = generate_changelog(changes, now)

    print(f"[sync_notes] 变更条目: {len(changes)}")

    # 始终追加到 NOTES.md（保持历史记录）
    append_to_notes(changelog)

    # 同时追加到当日工作日志（文件变更 + git commit）
    append_to_worklog(changes, now)

    # 保存新快照
    save_snapshot(new_structure)

    print(f"[sync_notes] 完成，变更已写入 NOTES.md 和 work_logs/{date.today()}.md")


if __name__ == "__main__":
    main()