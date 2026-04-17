from __future__ import annotations

import json
import shlex
import subprocess
from pathlib import Path

DEFAULT_PROGRAMS = [
    {
        "id": "focus-timer",
        "name": "专注计时器",
        "summary": "一个轻量的番茄钟工具，支持自定义时长与阶段提醒。",
        "stack": ["Vue 3", "Tailwind CSS"],
        "status": "进行中",
    },
    {
        "id": "daily-notes",
        "name": "每日随记",
        "summary": "简洁的日记记录应用，强调快速输入和回顾体验。",
        "stack": ["Flask", "SQLite"],
        "status": "维护中",
    },
    {
        "id": "image-cleanup",
        "name": "图片整理助手",
        "summary": "用于批量重命名与归档图片素材的小工具。",
        "stack": ["Python"],
        "status": "规划中",
    },
]

DEFAULT_BLOGS = [
    {
        "id": "welcome-blog",
        "title": "欢迎来到站内博客",
        "content": "这是第一篇站内博客内容，你可以在后续阶段新增、编辑和删除博客。",
        "tags": ["公告", "博客"],
        "isFavorite": False,
        "createdAt": "2026-04-12T00:00:00Z",
        "updatedAt": "2026-04-12T00:00:00Z",
    }
]

DATA_FILE_PATH = Path(__file__).resolve().parents[1] / "data.json"


def _default_programs():
    return [dict(item) for item in DEFAULT_PROGRAMS]


def _default_blogs():
    return [dict(item) for item in DEFAULT_BLOGS]


def _load_data():
    if not DATA_FILE_PATH.exists():
        return _default_programs(), [], _default_blogs()

    try:
        with DATA_FILE_PATH.open("r", encoding="utf-8") as data_file:
            payload = json.load(data_file)
    except (json.JSONDecodeError, OSError):
        return _default_programs(), [], _default_blogs()

    if not isinstance(payload, dict):
        return _default_programs(), [], _default_blogs()

    programs = payload.get("programs", [])
    fun_items = payload.get("fun", [])
    blogs = payload.get("blogs", _default_blogs())
    if not isinstance(programs, list) or not isinstance(fun_items, list) or not isinstance(blogs, list):
        return _default_programs(), [], _default_blogs()

    normalized_programs = [item for item in programs if isinstance(item, dict)]
    normalized_fun_items = [item for item in fun_items if isinstance(item, dict)]
    normalized_blogs = [item for item in blogs if isinstance(item, dict)]
    return normalized_programs, normalized_fun_items, normalized_blogs


PROGRAMS, FUN_ITEMS, BLOGS = _load_data()


def _save_data():
    payload = {"programs": PROGRAMS, "fun": FUN_ITEMS, "blogs": BLOGS}
    with DATA_FILE_PATH.open("w", encoding="utf-8") as data_file:
        json.dump(payload, data_file, ensure_ascii=False, indent=2)


def get_programs():
    return PROGRAMS


def get_program_by_id(program_id: str):
    return next((item for item in PROGRAMS if item["id"] == program_id), None)


def add_program(program: dict):
    PROGRAMS.insert(0, program)
    _save_data()
    return program


def add_fun_item(fun_item: dict):
    FUN_ITEMS.insert(0, fun_item)
    _save_data()
    return fun_item


def get_fun_items():
    return FUN_ITEMS


def get_blogs():
    return BLOGS


def get_blog_by_id(blog_id: str):
    return next((item for item in BLOGS if item.get("id") == blog_id), None)


BLOCKED_COMMANDS = {
    "rm",
    "rmdir",
    "mv",
    "dd",
    "shutdown",
    "reboot",
    "mkfs",
    "chmod",
    "chown",
    "curl",
    "wget",
    "scp",
    "ssh",
    "pip",
    "npm",
    "yarn",
}
BLOCKED_TOKENS = {"&&", "||", ";", "|", ">", ">>", "<", "$(", "`"}


def _normalize_command(command: str | list[str]) -> list[str]:
    if isinstance(command, str):
        tokens = shlex.split(command)
    elif isinstance(command, list) and all(isinstance(item, str) for item in command):
        tokens = command
    else:
        raise ValueError("command must be a string or a list of strings")

    if not tokens:
        raise ValueError("command is empty")

    joined = " ".join(tokens)
    if any(token in joined for token in BLOCKED_TOKENS):
        raise ValueError("dangerous command token detected")

    executable = tokens[0].strip().lower()
    if executable in BLOCKED_COMMANDS:
        raise ValueError(f"command '{executable}' is not allowed")

    return tokens


def run_command(command: str | list[str], timeout: int = 2):
    try:
        safe_command = _normalize_command(command)
        completed = subprocess.run(
            safe_command,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
            shell=False,
        )
        return {
            "success": completed.returncode == 0,
            "returncode": completed.returncode,
            "stdout": completed.stdout.strip(),
            "stderr": completed.stderr.strip(),
            "timed_out": False,
        }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "returncode": None,
            "stdout": "",
            "stderr": "command timed out",
            "timed_out": True,
        }
    except Exception as exc:  # noqa: BLE001
        return {
            "success": False,
            "returncode": None,
            "stdout": "",
            "stderr": str(exc),
            "timed_out": False,
        }
