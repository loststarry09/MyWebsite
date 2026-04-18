import json
from datetime import datetime
from pathlib import Path

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import event

# 全局数据库实例，供模型和应用共享
db = SQLAlchemy()
DATABASE_URI = "sqlite:///blog.db"
MIGRATION_MARKER_KEY = "json_to_sqlite_blog_migration_v1"
LEGACY_DATA_JSON_PATH = Path(__file__).resolve().parents[1] / "data.json"
LEGACY_BLOGS_JSON_PATH = Path(__file__).resolve().parents[1] / "blogs.json"


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


def init_db(app: Flask) -> None:
    """初始化 SQLite 与 SQLAlchemy，并自动建库建表。"""
    app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {"connect_args": {"timeout": 30}}
    db.init_app(app)

    with app.app_context():
        import models  # noqa: F401

        if app.config["SQLALCHEMY_DATABASE_URI"].startswith("sqlite:") and not app.extensions.get(
            "sqlite_pragmas_registered", False
        ):
            event.listen(db.engine, "connect", _set_sqlite_pragma)
            app.extensions["sqlite_pragmas_registered"] = True

        db.create_all()
        _migrate_legacy_json_blogs()
