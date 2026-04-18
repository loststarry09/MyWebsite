from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# 全局数据库实例，供模型和应用共享
db = SQLAlchemy()
DATABASE_URI = "sqlite:///blog.db"


def init_db(app: Flask) -> None:
    """初始化 SQLite 与 SQLAlchemy，并自动建库建表。"""
    app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)

    with app.app_context():
        import models  # noqa: F401

        db.create_all()
