import logging
from functools import wraps
from datetime import datetime, timezone

from flask import Blueprint, jsonify, request
from sqlalchemy import or_
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import selectinload

from database.db import db
from models.blog import Blog, Tag

blog_bp = Blueprint("blog", __name__)
logger = logging.getLogger(__name__)
DEFAULT_PAGE = 1
DEFAULT_PAGE_SIZE = 10
MAX_PAGE = 10000
MAX_PAGE_SIZE = 100
MAX_CONTENT_LENGTH = 20000


def _normalize_tags(tags):
    if isinstance(tags, list):
        return [str(tag).strip() for tag in tags if str(tag).strip()]
    if isinstance(tags, str):
        return [item.strip() for item in tags.replace("，", ",").split(",") if item.strip()]
    return []


def _to_iso(dt: datetime | None) -> str | None:
    if dt is None:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _serialize_blog(blog: Blog) -> dict:
    return {
        "id": blog.id,
        "title": blog.title,
        "content": blog.content,
        "tags": [tag.name for tag in blog.tags],
        "isFavorite": bool(blog.is_favorite),
        "isPublished": bool(blog.is_published),
        "views": int(blog.views or 0),
        "createdAt": _to_iso(blog.created_at),
        "updatedAt": _to_iso(blog.updated_at),
    }


def _resolve_tags(tags) -> list[Tag]:
    names = list(dict.fromkeys(_normalize_tags(tags)))
    if not names:
        return []

    stmt = sqlite_insert(Tag).values([{"name": name} for name in names]).on_conflict_do_nothing(index_elements=["name"])
    db.session.execute(stmt)
    existing_tags = Tag.query.filter(Tag.name.in_(names)).all()
    existing_map = {tag.name: tag for tag in existing_tags}
    return [existing_map[name] for name in names if name in existing_map]


def _parse_blog_id(blog_id: str) -> int | None:
    try:
        return int(blog_id)
    except (TypeError, ValueError):
        return None


def _invalid_blog_id_response():
    return _error_response("invalid_id", "Blog ID must be a valid integer", 400, code="INVALID_ID")


def _error_response(error: str, message: str, status: int, code: str | None = None):
    payload = {"success": False, "data": None, "message": message, "error": error}
    if code:
        payload["code"] = code
    return jsonify(payload), status


def _success_response(data, message: str = "", status: int = 200):
    return jsonify({"success": True, "data": data, "message": message}), status


def _safe_route(handler):
    @wraps(handler)
    def wrapper(*args, **kwargs):
        try:
            return handler(*args, **kwargs)
        except SQLAlchemyError:
            db.session.rollback()
            logger.exception("Database error on %s", request.path)
            return _error_response("db_error", "数据库操作失败，请稍后重试", 500, code="DATABASE_ERROR")
        except Exception:
            logger.exception("Unhandled error on %s", request.path)
            return _error_response("internal_error", "服务器内部错误", 500, code="INTERNAL_ERROR")

    return wrapper


def _validate_title(value):
    if not isinstance(value, str) or not value.strip():
        return "字段 title 不能为空"
    return None


def _validate_content(value):
    if value is None:
        return None
    if not isinstance(value, str):
        return "字段 content 必须是字符串"
    if len(value) > MAX_CONTENT_LENGTH:
        return f"字段 content 长度不能超过 {MAX_CONTENT_LENGTH} 个字符"
    return None


def _parse_bool_with_status(value):
    if isinstance(value, bool):
        return value, True
    if isinstance(value, int) and value in {0, 1}:
        return bool(value), True
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"true", "1", "yes", "on"}:
            return True, True
        if normalized in {"false", "0", "no", "off"}:
            return False, True
    return None, False


def _parse_bool_arg(name: str) -> bool | None:
    raw = request.args.get(name)
    if raw is None:
        return None
    value = raw.strip().lower()
    if value in {"true", "1", "yes", "on"}:
        return True
    if value in {"false", "0", "no", "off"}:
        return False
    return None


def _parse_int_arg(name: str, default: int, minimum: int, maximum: int) -> int:
    raw = request.args.get(name)
    if raw is None:
        return default
    try:
        value = int(raw.strip())
    except (TypeError, ValueError):
        return default
    if value < minimum:
        return minimum
    if value > maximum:
        return maximum
    return value


@blog_bp.get("/blogs")
@_safe_route
def list_blogs():
    tag = request.args.get("tag", "").strip()
    keyword = request.args.get("keyword", "").strip()
    favorite = _parse_bool_arg("favorite")
    page = _parse_int_arg("page", default=DEFAULT_PAGE, minimum=1, maximum=MAX_PAGE)
    page_size = _parse_int_arg("pageSize", default=DEFAULT_PAGE_SIZE, minimum=1, maximum=MAX_PAGE_SIZE)
    offset = (page - 1) * page_size

    # 预加载 tags，避免列表序列化时逐条触发关联查询（N+1）。
    query = Blog.query.options(selectinload(Blog.tags))
    if tag:
        query = query.join(Blog.tags).filter(Tag.name == tag)
    if keyword:
        like_pattern = f"%{keyword}%"
        query = query.filter(or_(Blog.title.ilike(like_pattern), Blog.content.ilike(like_pattern)))
    if favorite is not None:
        query = query.filter(Blog.is_favorite.is_(favorite))

    blogs = query.order_by(Blog.created_at.desc(), Blog.id.desc()).offset(offset).limit(page_size).all()
    return _success_response([_serialize_blog(blog) for blog in blogs])


@blog_bp.get("/blog")
@_safe_route
def list_blogs_compat():
    """兼容单数路径 /api/blog，实际复用 /api/blogs 的列表查询逻辑。"""
    return list_blogs()


@blog_bp.get("/blog/")
@_safe_route
def get_blog_by_query():
    blog_id = request.args.get("id", "").strip()
    if not blog_id:
        return _error_response(
            "missing_blog_id",
            "请通过查询参数 id 提供博客 ID，例如 /api/blog/?id=1",
            400,
            code="MISSING_BLOG_ID",
        )

    blog_pk = _parse_blog_id(blog_id)
    if blog_pk is None:
        return _invalid_blog_id_response()

    blog = db.session.get(Blog, blog_pk)
    if blog is None:
        return _error_response("not_found", f"Blog '{blog_id}' not found", 404, code="NOT_FOUND")
    return _success_response(_serialize_blog(blog))


@blog_bp.get("/blog/<blog_id>")
@_safe_route
def get_blog(blog_id: str):
    blog_pk = _parse_blog_id(blog_id)
    if blog_pk is None:
        return _invalid_blog_id_response()

    blog = db.session.get(Blog, blog_pk)
    if blog is None:
        return _error_response("not_found", f"Blog '{blog_id}' not found", 404, code="NOT_FOUND")

    Blog.query.filter(Blog.id == blog_pk).update({"views": Blog.views + 1}, synchronize_session=False)
    db.session.commit()
    db.session.refresh(blog)
    return _success_response(_serialize_blog(blog))


@blog_bp.post("/blog")
@_safe_route
def create_blog():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return _error_response("invalid_json", "请求体必须是 JSON 对象", 400, code="INVALID_JSON")

    title = payload.get("title", "")
    title_error = _validate_title(title)
    if title_error:
        return _error_response("validation_error", title_error, 400, code="VALIDATION_ERROR")

    content = payload.get("content", "")
    content_error = _validate_content(content)
    if content_error:
        return _error_response("validation_error", content_error, 400, code="VALIDATION_ERROR")
    if content is None:
        content = ""

    views_value = payload.get("views", 0)
    try:
        views = int(views_value or 0)
    except (ValueError, TypeError):
        return _error_response("validation_error", "字段 views 必须是数字", 400, code="VALIDATION_ERROR")

    is_favorite, is_favorite_ok = _parse_bool_with_status(payload.get("isFavorite", False))
    if not is_favorite_ok:
        return _error_response("validation_error", "字段 isFavorite 必须是布尔值", 400, code="VALIDATION_ERROR")

    is_published, is_published_ok = _parse_bool_with_status(payload.get("isPublished", False))
    if not is_published_ok:
        return _error_response("validation_error", "字段 isPublished 必须是布尔值", 400, code="VALIDATION_ERROR")

    blog = Blog(
        title=title.strip(),
        content=content if isinstance(content, str) else "",
        is_favorite=is_favorite,
        is_published=is_published,
        views=views,
    )
    blog.tags = _resolve_tags(payload.get("tags"))
    db.session.add(blog)
    db.session.commit()
    logger.info("blog_created id=%s title=%s", blog.id, blog.title)

    return _success_response(_serialize_blog(blog), status=201)


@blog_bp.put("/blog/<blog_id>")
@_safe_route
def update_blog(blog_id: str):
    blog_pk = _parse_blog_id(blog_id)
    if blog_pk is None:
        return _invalid_blog_id_response()

    blog = db.session.get(Blog, blog_pk)
    if blog is None:
        return _error_response("not_found", f"Blog '{blog_id}' not found", 404, code="NOT_FOUND")

    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return _error_response("invalid_json", "请求体必须是 JSON 对象", 400, code="INVALID_JSON")

    if "title" in payload:
        title_error = _validate_title(payload["title"])
        if title_error:
            return _error_response("validation_error", title_error, 400, code="VALIDATION_ERROR")
        blog.title = payload["title"].strip()

    if "content" in payload:
        content_error = _validate_content(payload["content"])
        if content_error:
            return _error_response("validation_error", content_error, 400, code="VALIDATION_ERROR")
        blog.content = payload["content"] if isinstance(payload["content"], str) else ""

    if "tags" in payload:
        blog.tags = _resolve_tags(payload["tags"])

    if "isFavorite" in payload:
        is_favorite, is_favorite_ok = _parse_bool_with_status(payload["isFavorite"])
        if not is_favorite_ok:
            return _error_response("validation_error", "字段 isFavorite 必须是布尔值", 400, code="VALIDATION_ERROR")
        blog.is_favorite = is_favorite

    if "isPublished" in payload:
        is_published, is_published_ok = _parse_bool_with_status(payload["isPublished"])
        if not is_published_ok:
            return _error_response("validation_error", "字段 isPublished 必须是布尔值", 400, code="VALIDATION_ERROR")
        blog.is_published = is_published

    if "views" in payload:
        try:
            blog.views = int(payload["views"] or 0)
        except (TypeError, ValueError):
            return _error_response("validation_error", "字段 views 必须是数字", 400, code="VALIDATION_ERROR")

    db.session.commit()
    logger.info("blog_updated id=%s", blog.id)

    return _success_response(_serialize_blog(blog))


@blog_bp.delete("/blog/<blog_id>")
@_safe_route
def delete_blog(blog_id: str):
    blog_pk = _parse_blog_id(blog_id)
    if blog_pk is None:
        return _invalid_blog_id_response()

    blog = db.session.get(Blog, blog_pk)
    if blog is None:
        return _error_response("not_found", f"Blog '{blog_id}' not found", 404, code="NOT_FOUND")

    deleted = _serialize_blog(blog)
    db.session.delete(blog)
    db.session.commit()
    logger.info("blog_deleted id=%s", blog_pk)
    return _success_response({"deleted": True, "blog": deleted})
