import os
from pathlib import Path
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.engine.url import make_url
from sqlalchemy.orm import Session, declarative_base, sessionmaker

# 生产默认数据库绝对路径（必须使用 sqlite://// 形式）。
DEFAULT_DATABASE_URL = "sqlite:////home/admin/program/MyWebsite/database/blog.db"


def _resolve_database_url() -> str:
    """读取并标准化数据库连接串，默认使用生产绝对路径。"""

    raw = os.getenv("SQLALCHEMY_DATABASE_URI", DEFAULT_DATABASE_URL).strip()
    if not raw:
        return DEFAULT_DATABASE_URL
    return raw


def _validate_sqlite_url(database_url: str) -> None:
    """保护性校验：SQLite 绝对路径必须使用 4 个斜杠。"""

    url = make_url(database_url)
    if not url.drivername.startswith("sqlite"):
        return

    if not url.database:
        raise RuntimeError("Invalid SQLite database URL: database path is empty.")
    if url.database == ":memory:":
        return

    db_path = Path(url.database).expanduser()
    if db_path.is_absolute() and not database_url.startswith("sqlite:////"):
        raise RuntimeError(
            "SQLite absolute path must start with 'sqlite:////' (4 slashes), "
            f"got: {database_url}"
        )


DATABASE_URL = _resolve_database_url()
_validate_sqlite_url(DATABASE_URL)

connect_args = {"check_same_thread": False, "timeout": 30} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, pool_pre_ping=True, connect_args=connect_args)

# 每次请求使用独立 Session，配合 get_db 自动回收，避免连接泄漏和锁死。
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """FastAPI 依赖注入入口：在请求结束后自动关闭数据库会话。"""

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

