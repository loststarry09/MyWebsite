from __future__ import annotations

import os
from pathlib import Path


class Settings:
    """全局配置中心：统一管理路径与数据库连接串。"""

    def __init__(self) -> None:
        # 统一根路径（默认保持“极简无痛流”生产目录）
        base_path_raw = os.getenv("MYWEBSITE_BASE_PATH", "/home/admin/program/MyWebsite").strip()
        self.BASE_PATH = Path(base_path_raw).expanduser()

        # 数据库文件路径：优先显式配置 DATABASE_PATH，其次使用 BASE_PATH/database/blog.db
        database_path_raw = os.getenv("DATABASE_PATH", str(self.BASE_PATH / "database" / "blog.db")).strip()
        self.DATABASE_PATH = Path(database_path_raw).expanduser()

        # 数据库连接串：优先 SQLALCHEMY_DATABASE_URI，否则基于 DATABASE_PATH 生成 sqlite URL
        default_database_url = f"sqlite:///{self.DATABASE_PATH}"
        self.DATABASE_URL = os.getenv("SQLALCHEMY_DATABASE_URI", default_database_url).strip() or default_database_url

        # 上传目录：优先 UPLOAD_DIR，兼容历史 IMAGE_UPLOAD_DIR，默认 BASE_PATH/uploads
        upload_dir_raw = (
            os.getenv("UPLOAD_DIR")
            or os.getenv("IMAGE_UPLOAD_DIR")
            or str(self.BASE_PATH / "uploads")
        )
        self.UPLOAD_DIR = Path(upload_dir_raw).expanduser()


settings = Settings()
