from datetime import datetime, timezone

from database.db import db


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Blog(db.Model):
    __tablename__ = "blogs"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=_utc_now)
    updated_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=_utc_now,
        onupdate=_utc_now,
    )
    is_favorite = db.Column(db.Boolean, nullable=False, default=False)
    is_published = db.Column(db.Boolean, nullable=False, default=False)
    views = db.Column(db.Integer, nullable=False, default=0)

    tags = db.relationship(
        "Tag",
        secondary="blog_tags",
        back_populates="blogs",
    )


class Tag(db.Model):
    __tablename__ = "tags"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)

    blogs = db.relationship(
        "Blog",
        secondary="blog_tags",
        back_populates="tags",
    )


class BlogTag(db.Model):
    __tablename__ = "blog_tags"

    blog_id = db.Column(db.Integer, db.ForeignKey("blogs.id"), primary_key=True)
    tag_id = db.Column(db.Integer, db.ForeignKey("tags.id"), primary_key=True)

    blog = db.relationship("Blog")
    tag = db.relationship("Tag")
