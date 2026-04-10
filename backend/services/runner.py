from __future__ import annotations

import shlex
import subprocess

PROGRAMS = [
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


def get_programs():
    return PROGRAMS


def get_program_by_id(program_id: str):
    return next((item for item in PROGRAMS if item["id"] == program_id), None)


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
