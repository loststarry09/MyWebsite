import json
import os
from threading import Lock
from datetime import datetime
from pathlib import Path

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import event
from sqlalchemy.engine.url import make_url

# 全局数据库实例，供模型和应用共享
db = SQLAlchemy()
EXPECTED_DB_PATH = Path("/home/admin/program/MyWebsite/database/blog.db")
LEGACY_DB_PATH = Path("/home/admin/program/MyWebsite/code/backend/blog.db")
LEGACY_DB_DIR = LEGACY_DB_PATH.parent
MIGRATION_MARKER_KEY = "json_to_sqlite_blog_migration_v1"
LEGACY_DATA_JSON_PATH = Path(__file__).resolve().parents[1] / "data.json"
LEGACY_BLOGS_JSON_PATH = Path(__file__).resolve().parents[1] / "blogs.json"
_SQLITE_PRAGMA_LISTENER_LOCK = Lock()


def _set_sqlite_pragma(dbapi_connection, _connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA synchronous=NORMAL")
    cursor.close()


def _normalize_tags(tags) -> list[str]:
    if isinstance(tags, list):
        normalized = [str(tag).strip() for tag in tags if str(tag).strip()]
    elif isinstance(tags, str):
        normalized = [item.strip() for item in tags.replace("，", ",").split(",") if item.strip()]
    else:
        normalized = []
    return list(dict.fromkeys(normalized))


def _safe_int(value, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _parse_iso_datetime(value):
    if not isinstance(value, str) or not value.strip():
        return None
    raw = value.strip().replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(raw)
    except ValueError:
        return None


def _load_legacy_blogs() -> list[dict]:
    if LEGACY_DATA_JSON_PATH.exists():
        try:
            payload = json.loads(LEGACY_DATA_JSON_PATH.read_text(encoding="utf-8"))
            if isinstance(payload, dict) and isinstance(payload.get("blogs"), list):
                return [item for item in payload["blogs"] if isinstance(item, dict)]
        except (OSError, json.JSONDecodeError):
            pass

    if LEGACY_BLOGS_JSON_PATH.exists():
        try:
            payload = json.loads(LEGACY_BLOGS_JSON_PATH.read_text(encoding="utf-8"))
            if isinstance(payload, list):
                return [item for item in payload if isinstance(item, dict)]
        except (OSError, json.JSONDecodeError):
            pass

    return []


def _migrate_legacy_json_blogs() -> None:
    from models import Blog, MigrationState, Tag

    if db.session.get(MigrationState, MIGRATION_MARKER_KEY) is not None:
        return

    if Blog.query.count() > 0:
        return

    if not LEGACY_DATA_JSON_PATH.exists() and not LEGACY_BLOGS_JSON_PATH.exists():
        return

    legacy_blogs = _load_legacy_blogs()
    if not legacy_blogs:
        return

    tag_cache = {tag.name: tag for tag in Tag.query.all()}

    try:
        for legacy in legacy_blogs:
            title = legacy.get("title", "")
            if not isinstance(title, str) or not title.strip():
                continue

            blog = Blog(
                title=title.strip(),
                content=legacy.get("content", "") if isinstance(legacy.get("content"), str) else "",
                is_favorite=bool(legacy.get("isFavorite", False)),
                is_published=bool(legacy.get("isPublished", False)),
                views=_safe_int(legacy.get("views", 0), 0),
            )

            created_at = _parse_iso_datetime(legacy.get("createdAt"))
            updated_at = _parse_iso_datetime(legacy.get("updatedAt"))
            if created_at is not None:
                blog.created_at = created_at
            if updated_at is not None:
                blog.updated_at = updated_at

            resolved_tags = []
            for name in _normalize_tags(legacy.get("tags")):
                tag = tag_cache.get(name)
                if tag is None:
                    tag = Tag(name=name)
                    db.session.add(tag)
                    tag_cache[name] = tag
                resolved_tags.append(tag)

            blog.tags = resolved_tags
            db.session.add(blog)

        db.session.add(MigrationState(key=MIGRATION_MARKER_KEY, value="done"))
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise


def _resolve_sqlite_db_path(database_uri: str) -> Path | None:
    url = make_url(database_uri)
    if not url.drivername.startswith("sqlite"):
        return None
    if not url.database:
        raise RuntimeError(f"Invalid SQLite database URI: {database_uri}")
    db_path = Path(url.database).expanduser()
    return db_path.resolve()


def _assert_database_uri_is_safe(database_uri: str) -> None:
    sqlite_path = _resolve_sqlite_db_path(database_uri)
    if sqlite_path is None:
        return
    if sqlite_path == LEGACY_DB_PATH or LEGACY_DB_DIR in sqlite_path.parents:
        raise RuntimeError(f"Fatal: legacy SQLite path detected: {sqlite_path}")
    if sqlite_path != EXPECTED_DB_PATH:
        raise RuntimeError(f"Fatal: SQLite path mismatch: {sqlite_path}, expected: {EXPECTED_DB_PATH}")


def _assert_sqlite_uri_and_dir_permissions(database_uri: str) -> None:
    url = make_url(database_uri)
    if not url.drivername.startswith("sqlite"):
        return

    database = url.database
    if not database:
        raise RuntimeError("Fatal: SQLite URI is invalid because database path is empty.")
    if database == ":memory:":
        return

    sqlite_path = Path(database).expanduser()
    # Linux absolute SQLite path must use sqlite:////... (4 slashes).
    if sqlite_path.is_absolute() and not database_uri.startswith("sqlite:////"):
        raise RuntimeError(
            "Fatal: SQLite absolute path must start with 'sqlite:////' (4 slashes), "
            f"got: {database_uri}"
        )

    sqlite_dir = sqlite_path.resolve().parent
    if not sqlite_dir.exists():
        raise RuntimeError(f"Fatal: SQLite directory does not exist: {sqlite_dir}")
    if not os.access(sqlite_dir, os.W_OK):
        raise RuntimeError(
            f"Fatal: SQLite directory is not writable: {sqlite_dir}. "
            "Please grant write permission to the runtime user."
        )


def init_db(app: Flask) -> None:
    """初始化 SQLite 与 SQLAlchemy，并自动建库建表。"""
    raw_database_uri = os.getenv("SQLALCHEMY_DATABASE_URI")
    if raw_database_uri is None or not raw_database_uri.strip():
        raise RuntimeError("Fatal: SQLALCHEMY_DATABASE_URI is required and cannot be empty.")
    database_uri = raw_database_uri.strip()
    sqlite_path = _resolve_sqlite_db_path(database_uri)
    if sqlite_path is not None:
        app.logger.info(f"Resolved SQLite absolute path: {sqlite_path}")
    _assert_sqlite_uri_and_dir_permissions(database_uri)
    _assert_database_uri_is_safe(database_uri)
    app.config["SQLALCHEMY_DATABASE_URI"] = database_uri
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {"connect_args": {"timeout": 30}}
    app.logger.info(f"Using database at: {app.config['SQLALCHEMY_DATABASE_URI']}")
    db.init_app(app)

    with app.app_context():
        import models  # noqa: F401

        if app.config["SQLALCHEMY_DATABASE_URI"].startswith("sqlite:"):
            with _SQLITE_PRAGMA_LISTENER_LOCK:
                if not app.extensions.get("sqlite_pragmas_registered", False):
                    event.listen(db.engine, "connect", _set_sqlite_pragma)
                    app.extensions["sqlite_pragmas_registered"] = True

        db.create_all()
        _migrate_legacy_json_blogs()
