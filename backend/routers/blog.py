import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from fastapi.responses import JSONResponse
from sqlalchemy import or_, select, update
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.orm import Session, selectinload

from config import settings
from fastapi_core.database import get_db
from fastapi_core.models import Blog, Tag
from fastapi_core.schemas import BlogCreateSchema, BlogUpdateSchema

router = APIRouter(prefix="/api")

DEFAULT_PAGE = 1
DEFAULT_PAGE_SIZE = 10
MAX_PAGE = 10000
MAX_PAGE_SIZE = 100
IMAGE_UPLOAD_DIR = settings.UPLOAD_DIR
IMAGE_MAX_SIZE_BYTES = 5 * 1024 * 1024
ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
ALLOWED_IMAGE_CONTENT_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}


def _raise_http_error(error: str, message: str, status: int, code: str | None = None) -> None:
    detail = {"error": error, "message": message}
    if code:
        detail["code"] = code
    raise HTTPException(status_code=status, detail=detail)


def _success_response(data: Any, message: str = "", status: int = 200) -> JSONResponse:
    return JSONResponse(content={"success": True, "data": data, "message": message}, status_code=status)


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


def _parse_blog_id(blog_id: str) -> int | None:
    try:
        return int(blog_id)
    except (TypeError, ValueError):
        return None


def _normalize_tags(tags: list[str] | str | None) -> list[str]:
    if isinstance(tags, list):
        return [str(tag).strip() for tag in tags if str(tag).strip()]
    if isinstance(tags, str):
        return [item.strip() for item in tags.replace("，", ",").split(",") if item.strip()]
    return []


def _resolve_tags(db_session: Session, tags: list[str] | str | None) -> list[Tag]:
    names = list(dict.fromkeys(_normalize_tags(tags)))
    if not names:
        return []

    stmt = sqlite_insert(Tag).values([{"name": name} for name in names]).on_conflict_do_nothing(index_elements=["name"])
    db_session.execute(stmt)
    tag_rows = db_session.execute(select(Tag).where(Tag.name.in_(names))).scalars().all()
    tag_map = {tag.name: tag for tag in tag_rows}
    return [tag_map[name] for name in names if name in tag_map]


def _parse_bool_arg(raw: str | None) -> bool | None:
    if raw is None:
        return None
    value = raw.strip().lower()
    if value in {"true", "1", "yes", "on"}:
        return True
    if value in {"false", "0", "no", "off"}:
        return False
    return None


def _safe_page(value: int, minimum: int, maximum: int) -> int:
    if value < minimum:
        return minimum
    if value > maximum:
        return maximum
    return value


def _raise_invalid_blog_id_error() -> None:
    _raise_http_error("invalid_id", "博客 ID 必须是有效整数", 400, code="INVALID_ID")


@router.get("/blogs")
def list_blogs(
    tag: str = Query("", description="按标签筛选"),
    keyword: str = Query("", description="按关键字筛选"),
    favorite: str | None = Query(default=None, description="是否收藏"),
    page: int = Query(DEFAULT_PAGE),
    page_size: int = Query(DEFAULT_PAGE_SIZE, alias="pageSize"),
    db_session: Session = Depends(get_db),
):
    parsed_favorite = _parse_bool_arg(favorite)
    page = _safe_page(page, minimum=1, maximum=MAX_PAGE)
    page_size = _safe_page(page_size, minimum=1, maximum=MAX_PAGE_SIZE)
    offset = (page - 1) * page_size

    query = select(Blog).options(selectinload(Blog.tags))
    if tag.strip():
        query = query.join(Blog.tags).where(Tag.name == tag.strip())
    if keyword.strip():
        like_pattern = f"%{keyword.strip()}%"
        query = query.where(or_(Blog.title.ilike(like_pattern), Blog.content.ilike(like_pattern)))
    if parsed_favorite is not None:
        query = query.where(Blog.is_favorite.is_(parsed_favorite))

    blogs = db_session.execute(query.order_by(Blog.created_at.desc(), Blog.id.desc()).offset(offset).limit(page_size)).scalars().all()
    return _success_response([_serialize_blog(blog) for blog in blogs])


@router.get("/blog")
def list_blogs_compat(
    tag: str = Query(""),
    keyword: str = Query(""),
    favorite: str | None = Query(default=None),
    page: int = Query(DEFAULT_PAGE),
    page_size: int = Query(DEFAULT_PAGE_SIZE, alias="pageSize"),
    db_session: Session = Depends(get_db),
):
    return list_blogs(tag=tag, keyword=keyword, favorite=favorite, page=page, page_size=page_size, db_session=db_session)


@router.get("/blog/")
def get_blog_by_query(blog_id_query: str = Query(default="", alias="id"), db_session: Session = Depends(get_db)):
    blog_id = blog_id_query.strip()
    if not blog_id:
        _raise_http_error(
            "missing_blog_id",
            "请通过查询参数 id 提供博客 ID，例如 /api/blog/?id=1",
            400,
            code="MISSING_BLOG_ID",
        )

    blog_pk = _parse_blog_id(blog_id)
    if blog_pk is None:
        _raise_invalid_blog_id_error()

    blog = db_session.get(Blog, blog_pk)
    if blog is None:
        _raise_http_error("not_found", f"未找到 ID 为 {blog_id} 的博客", 404, code="NOT_FOUND")
    return _success_response(_serialize_blog(blog))


@router.get("/blog/{blog_id}")
def get_blog(blog_id: str, db_session: Session = Depends(get_db)):
    blog_pk = _parse_blog_id(blog_id)
    if blog_pk is None:
        _raise_invalid_blog_id_error()

    blog = db_session.get(Blog, blog_pk)
    if blog is None:
        _raise_http_error("not_found", f"未找到 ID 为 {blog_id} 的博客", 404, code="NOT_FOUND")

    db_session.execute(update(Blog).where(Blog.id == blog_pk).values(views=Blog.views + 1))
    db_session.commit()
    db_session.refresh(blog)
    return _success_response(_serialize_blog(blog))


@router.post("/blog")
def create_blog(blog_in: BlogCreateSchema, db_session: Session = Depends(get_db)):
    blog = Blog(
        title=blog_in.title,
        content=blog_in.content,
        is_favorite=blog_in.is_favorite,
        is_published=blog_in.is_published,
        views=blog_in.views,
    )
    blog.tags = _resolve_tags(db_session, blog_in.tags)
    db_session.add(blog)
    db_session.commit()
    db_session.refresh(blog)
    return _success_response(_serialize_blog(blog), status=201)


@router.put("/blog/{blog_id}")
def update_blog(blog_id: str, blog_in: BlogUpdateSchema, db_session: Session = Depends(get_db)):
    blog_pk = _parse_blog_id(blog_id)
    if blog_pk is None:
        _raise_invalid_blog_id_error()

    blog = db_session.get(Blog, blog_pk)
    if blog is None:
        _raise_http_error("not_found", f"未找到 ID 为 {blog_id} 的博客", 404, code="NOT_FOUND")

    update_payload = blog_in.model_dump(by_alias=True, exclude_unset=True)
    if "title" in update_payload:
        blog.title = update_payload["title"]
    if "content" in update_payload:
        blog.content = update_payload["content"] if update_payload["content"] is not None else ""
    if "tags" in update_payload:
        blog.tags = _resolve_tags(db_session, update_payload["tags"])
    if "isFavorite" in update_payload:
        blog.is_favorite = bool(update_payload["isFavorite"])
    if "isPublished" in update_payload:
        blog.is_published = bool(update_payload["isPublished"])
    if "views" in update_payload and update_payload["views"] is not None:
        blog.views = int(update_payload["views"])

    db_session.commit()
    db_session.refresh(blog)
    return _success_response(_serialize_blog(blog))


@router.delete("/blog/{blog_id}")
def delete_blog(blog_id: str, db_session: Session = Depends(get_db)):
    blog_pk = _parse_blog_id(blog_id)
    if blog_pk is None:
        _raise_invalid_blog_id_error()

    blog = db_session.get(Blog, blog_pk)
    if blog is None:
        _raise_http_error("not_found", f"未找到 ID 为 {blog_id} 的博客", 404, code="NOT_FOUND")

    deleted = _serialize_blog(blog)
    db_session.delete(blog)
    db_session.commit()
    return _success_response({"deleted": True, "blog": deleted})


@router.post("/upload_image")
async def upload_image(file: UploadFile = File(...)):
    filename = (file.filename or "").strip()
    if not filename:
        _raise_http_error("invalid_file", "上传文件名不能为空", 400, code="INVALID_FILE")

    extension = Path(filename).suffix.lower()
    if extension not in ALLOWED_IMAGE_EXTENSIONS:
        _raise_http_error(
            "invalid_file_type",
            "仅支持上传 jpg、jpeg、png、gif、webp 格式图片",
            400,
            code="INVALID_FILE_TYPE",
        )

    content_type = (file.content_type or "").lower()
    if content_type and content_type not in ALLOWED_IMAGE_CONTENT_TYPES:
        _raise_http_error(
            "invalid_file_type",
            "仅支持上传 jpg、jpeg、png、gif、webp 格式图片",
            400,
            code="INVALID_FILE_TYPE",
        )

    upload_root = IMAGE_UPLOAD_DIR.expanduser().resolve()
    upload_root.mkdir(parents=True, exist_ok=True)

    size = 0
    try:
        save_path: Path | None = None
        for attempt in range(3):
            candidate_name = f"{uuid.uuid4().hex}{extension}"
            candidate_path = (upload_root / candidate_name).resolve()
            if not candidate_path.is_relative_to(upload_root):
                _raise_http_error("invalid_file", "非法文件路径", 400, code="INVALID_FILE")
            try:
                with open(candidate_path, "xb") as target:
                    while True:
                        chunk = await file.read(1024 * 1024)
                        if not chunk:
                            break
                        size += len(chunk)
                        if size > IMAGE_MAX_SIZE_BYTES:
                            target.close()
                            candidate_path.unlink(missing_ok=True)
                            _raise_http_error(
                                "file_too_large",
                                "单张图片大小不能超过 5MB",
                                400,
                                code="FILE_TOO_LARGE",
                            )
                        target.write(chunk)
                save_path = candidate_path
                break
            except FileExistsError:
                if attempt == 2:
                    _raise_http_error("upload_failed", "图片保存失败，请稍后重试", 500, code="UPLOAD_FAILED")
                continue
        if save_path is None:
            _raise_http_error("upload_failed", "图片保存失败，请稍后重试", 500, code="UPLOAD_FAILED")
    finally:
        await file.close()

    image_url = f"/uploads/{save_path.name}"
    return _success_response({"url": image_url}, status=201)
