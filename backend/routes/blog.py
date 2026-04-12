from datetime import datetime, timezone
from time import time

from flask import Blueprint, jsonify, request

blog_bp = Blueprint("blog", __name__)

BLOGS = [
    {
        "id": "welcome-blog",
        "title": "欢迎来到站内博客",
        "content": "这是博客示例数据，后续可以通过 API 增删改查。",
        "tags": ["公告", "示例"],
        "isFavorite": True,
        "createdAt": "2026-04-12T00:00:00Z",
        "updatedAt": "2026-04-12T00:00:00Z",
    },
    {
        "id": "phase4-note",
        "title": "阶段4后端接口完成说明",
        "content": "本篇用于演示 Flask 博客 CRUD 接口的数据结构。",
        "tags": ["Flask", "API"],
        "isFavorite": False,
        "createdAt": "2026-04-12T00:00:00Z",
        "updatedAt": "2026-04-12T00:00:00Z",
    },
]


def _get_blog_index(blog_id: str):
    for index, blog in enumerate(BLOGS):
        if blog.get("id") == blog_id:
            return index
    return None


def _normalize_tags(tags):
    if isinstance(tags, list):
        return [str(tag).strip() for tag in tags if str(tag).strip()]
    if isinstance(tags, str):
        return [item.strip() for item in tags.replace("，", ",").split(",") if item.strip()]
    return []


def _now_iso():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


@blog_bp.get("/blogs")
def list_blogs():
    return jsonify(BLOGS)


@blog_bp.get("/blog/<blog_id>")
def get_blog(blog_id: str):
    blog_index = _get_blog_index(blog_id)
    if blog_index is None:
        return jsonify({"error": "not_found", "message": f"Blog '{blog_id}' not found"}), 404
    return jsonify(BLOGS[blog_index])


@blog_bp.post("/blog")
def create_blog():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify({"error": "invalid_json", "message": "请求体必须是 JSON 对象"}), 400

    title = payload.get("title", "")
    if not isinstance(title, str) or not title.strip():
        return jsonify({"error": "validation_error", "message": "字段 title 不能为空"}), 400

    now = int(time() * 1000)
    timestamp = _now_iso()
    blog = {
        "id": payload.get("id") if isinstance(payload.get("id"), str) and payload.get("id").strip() else f"blog-{now}",
        "title": title.strip(),
        "content": payload.get("content", "") if isinstance(payload.get("content"), str) else "",
        "tags": _normalize_tags(payload.get("tags")),
        "isFavorite": bool(payload.get("isFavorite", False)),
        "createdAt": payload.get("createdAt") if isinstance(payload.get("createdAt"), str) else timestamp,
        "updatedAt": payload.get("updatedAt") if isinstance(payload.get("updatedAt"), str) else timestamp,
    }
    BLOGS.insert(0, blog)
    return jsonify(blog), 201


@blog_bp.put("/blog/<blog_id>")
def update_blog(blog_id: str):
    blog_index = _get_blog_index(blog_id)
    if blog_index is None:
        return jsonify({"error": "not_found", "message": f"Blog '{blog_id}' not found"}), 404

    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify({"error": "invalid_json", "message": "请求体必须是 JSON 对象"}), 400

    current_blog = BLOGS[blog_index]

    if "title" in payload:
        if not isinstance(payload["title"], str) or not payload["title"].strip():
            return jsonify({"error": "validation_error", "message": "字段 title 不能为空"}), 400
        current_blog["title"] = payload["title"].strip()

    if "content" in payload and isinstance(payload["content"], str):
        current_blog["content"] = payload["content"]

    if "tags" in payload:
        current_blog["tags"] = _normalize_tags(payload["tags"])

    if "isFavorite" in payload:
        current_blog["isFavorite"] = bool(payload["isFavorite"])

    current_blog["updatedAt"] = payload["updatedAt"] if isinstance(payload.get("updatedAt"), str) else _now_iso()

    BLOGS[blog_index] = current_blog
    return jsonify(current_blog)


@blog_bp.delete("/blog/<blog_id>")
def delete_blog(blog_id: str):
    blog_index = _get_blog_index(blog_id)
    if blog_index is None:
        return jsonify({"error": "not_found", "message": f"Blog '{blog_id}' not found"}), 404

    deleted = BLOGS.pop(blog_index)
    return jsonify({"deleted": True, "blog": deleted})
