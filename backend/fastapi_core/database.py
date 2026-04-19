from pathlib import Path
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.engine.url import make_url
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from config import settings


def _resolve_database_url() -> str:
    """从配置中心读取数据库连接串，并做空值兜底校验。"""

    raw = settings.DATABASE_URL.strip()
    if not raw:
        raise RuntimeError("DATABASE_URL is empty in settings.")
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

# 每次请求使用独立 Session，并由依赖注入在请求结束后自动回收，避免连接泄漏。
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """FastAPI 依赖注入入口：在请求结束后自动关闭数据库会话。"""

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
