#!/usr/bin/env python3
"""
定时同步脚本：扫描项目结构与配置文件，将变更内容追加到 NOTES.md。
配合 systemd timer 每天执行，定时对比上次记录发现变更并更新。
"""
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
    "zhihuifangdong_all.py",
    "zhihuifangdong_fy",
    "zhihuifangdong_sy",
    "requirements.txt",
]


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
                    if "__pycache__" in f.parts or ".pytest_cache" in f.parts:
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


def append_to_worklog(changelog: str):
    """同时追加到当日工作日志"""
    today = date.today().strftime("%Y-%m-%d")
    log_file = WORK_LOGS_DIR / f"{today}.md"
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(changelog + "\n")


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

    # 同时追加到当日工作日志
    append_to_worklog(changelog)

    # 保存新快照
    save_snapshot(new_structure)

    print(f"[sync_notes] 完成，变更已写入 NOTES.md 和 work_logs/{date.today()}.md")


if __name__ == "__main__":
    main()