from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

MAX_CONTENT_LENGTH = 20000


def _normalize_tags(value: Any) -> list[str]:
    """兼容数组与逗号字符串两种标签入参。"""

    if value is None:
        return []
    if isinstance(value, str):
        return [item.strip() for item in value.replace("，", ",").split(",") if item.strip()]
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    raise ValueError("字段 tags 必须是字符串或字符串数组")


class BlogBaseSchema(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    title: str = Field(..., min_length=1, max_length=255, description="文章标题")
    content: str = Field("", max_length=MAX_CONTENT_LENGTH, description="文章正文")
    tags: list[str] = Field(default_factory=list, description="标签列表")
    is_favorite: bool = Field(False, alias="isFavorite", description="是否收藏")
    is_published: bool = Field(False, alias="isPublished", description="是否发布")
    views: int = Field(0, description="浏览量")

    @field_validator("title")
    @classmethod
    def _title_not_blank(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("字段 title 不能为空")
        return cleaned

    @field_validator("content", mode="before")
    @classmethod
    def _normalize_content(cls, value: Any) -> str:
        if value is None:
            return ""
        return value

    @field_validator("tags", mode="before")
    @classmethod
    def _validate_tags(cls, value: Any) -> list[str]:
        # 去重并保持原有顺序
        return list(dict.fromkeys(_normalize_tags(value)))


class BlogCreateSchema(BlogBaseSchema):
    """创建文章请求体。"""


class BlogUpdateSchema(BaseModel):
    """更新文章请求体（全部字段可选）。"""

    model_config = ConfigDict(populate_by_name=True)

    title: str | None = Field(None, min_length=1, max_length=255)
    content: str | None = Field(None, max_length=MAX_CONTENT_LENGTH)
    tags: list[str] | None = None
    is_favorite: bool | None = Field(None, alias="isFavorite")
    is_published: bool | None = Field(None, alias="isPublished")
    views: int | None = None

    @field_validator("title")
    @classmethod
    def _update_title_not_blank(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("字段 title 不能为空")
        return cleaned

    @field_validator("content")
    @classmethod
    def _update_content_normalize(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return value

    @field_validator("tags", mode="before")
    @classmethod
    def _update_tags_normalize(cls, value: Any) -> list[str] | None:
        if value is None:
            return None
        return list(dict.fromkeys(_normalize_tags(value)))


class BlogReadSchema(BaseModel):
    """文章响应体结构（保持前端兼容字段命名）。"""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    title: str
    content: str
    tags: list[str]
    is_favorite: bool = Field(alias="isFavorite")
    is_published: bool = Field(alias="isPublished")
    views: int
    created_at: datetime | None = Field(default=None, alias="createdAt")
    updated_at: datetime | None = Field(default=None, alias="updatedAt")
