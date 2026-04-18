from datetime import datetime, timezone

from flask import Blueprint, jsonify, request
from sqlalchemy.exc import IntegrityError

from database.db import db
from models.blog import Blog, Tag

blog_bp = Blueprint("blog", __name__)


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

    existing_tags = Tag.query.filter(Tag.name.in_(names)).all()
    existing_map = {tag.name: tag for tag in existing_tags}
    resolved: list[Tag] = []

    for name in names:
        tag = existing_map.get(name)
        if tag is None:
            tag = Tag(name=name)
            db.session.add(tag)
        resolved.append(tag)
    return resolved


def _parse_blog_id(blog_id: str) -> int | None:
    try:
        return int(blog_id)
    except (TypeError, ValueError):
        return None


@blog_bp.get("/blogs")
def list_blogs():
    blogs = Blog.query.order_by(Blog.created_at.desc(), Blog.id.desc()).all()
    return jsonify([_serialize_blog(blog) for blog in blogs])


@blog_bp.get("/blog/")
def get_blog_by_query():
    blog_id = request.args.get("id", "").strip()
    if not blog_id:
        return jsonify(
            {
                "error": "missing_blog_id",
                "message": "请通过查询参数 id 提供博客 ID，例如 /api/blog/?id=welcome-blog",
            }
        ), 400

    blog_pk = _parse_blog_id(blog_id)
    if blog_pk is None:
        return jsonify({"error": "not_found", "message": f"Blog '{blog_id}' not found"}), 404

    blog = Blog.query.get(blog_pk)
    if blog is None:
        return jsonify({"error": "not_found", "message": f"Blog '{blog_id}' not found"}), 404
    return jsonify(_serialize_blog(blog))


@blog_bp.get("/blog/<blog_id>")
def get_blog(blog_id: str):
    blog_pk = _parse_blog_id(blog_id)
    if blog_pk is None:
        return jsonify({"error": "not_found", "message": f"Blog '{blog_id}' not found"}), 404

    blog = Blog.query.get(blog_pk)
    if blog is None:
        return jsonify({"error": "not_found", "message": f"Blog '{blog_id}' not found"}), 404

    blog.views = int(blog.views or 0) + 1
    db.session.commit()
    return jsonify(_serialize_blog(blog))


@blog_bp.post("/blog")
def create_blog():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify({"error": "invalid_json", "message": "请求体必须是 JSON 对象"}), 400

    title = payload.get("title", "")
    if not isinstance(title, str) or not title.strip():
        return jsonify({"error": "validation_error", "message": "字段 title 不能为空"}), 400

    try:
        blog = Blog(
            title=title.strip(),
            content=payload.get("content", "") if isinstance(payload.get("content"), str) else "",
            is_favorite=bool(payload.get("isFavorite", False)),
            is_published=bool(payload.get("isPublished", False)),
            views=int(payload.get("views", 0) or 0),
        )
        blog.tags = _resolve_tags(payload.get("tags"))
        db.session.add(blog)
        db.session.commit()
    except (ValueError, TypeError, IntegrityError):
        db.session.rollback()
        return jsonify({"error": "persist_failed", "message": "博客保存失败，请稍后重试"}), 500

    return jsonify(_serialize_blog(blog)), 201


@blog_bp.put("/blog/<blog_id>")
def update_blog(blog_id: str):
    blog_pk = _parse_blog_id(blog_id)
    if blog_pk is None:
        return jsonify({"error": "not_found", "message": f"Blog '{blog_id}' not found"}), 404

    blog = Blog.query.get(blog_pk)
    if blog is None:
        return jsonify({"error": "not_found", "message": f"Blog '{blog_id}' not found"}), 404

    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify({"error": "invalid_json", "message": "请求体必须是 JSON 对象"}), 400

    if "title" in payload:
        if not isinstance(payload["title"], str) or not payload["title"].strip():
            return jsonify({"error": "validation_error", "message": "字段 title 不能为空"}), 400
        blog.title = payload["title"].strip()

    if "content" in payload and isinstance(payload["content"], str):
        blog.content = payload["content"]

    if "tags" in payload:
        blog.tags = _resolve_tags(payload["tags"])

    if "isFavorite" in payload:
        blog.is_favorite = bool(payload["isFavorite"])

    if "isPublished" in payload:
        blog.is_published = bool(payload["isPublished"])

    if "views" in payload:
        try:
            blog.views = int(payload["views"] or 0)
        except (TypeError, ValueError):
            return jsonify({"error": "validation_error", "message": "字段 views 必须是数字"}), 400

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "persist_failed", "message": "博客保存失败，请稍后重试"}), 500

    return jsonify(_serialize_blog(blog))


@blog_bp.delete("/blog/<blog_id>")
def delete_blog(blog_id: str):
    blog_pk = _parse_blog_id(blog_id)
    if blog_pk is None:
        return jsonify({"error": "not_found", "message": f"Blog '{blog_id}' not found"}), 404

    blog = Blog.query.get(blog_pk)
    if blog is None:
        return jsonify({"error": "not_found", "message": f"Blog '{blog_id}' not found"}), 404

    try:
        deleted = _serialize_blog(blog)
        db.session.delete(blog)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "persist_failed", "message": "博客保存失败，请稍后重试"}), 500
    return jsonify({"deleted": True, "blog": deleted})
