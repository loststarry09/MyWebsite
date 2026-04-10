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
