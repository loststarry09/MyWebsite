from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# 全局数据库实例，供模型和应用共享
db = SQLAlchemy()
SQLITE_URI = "sqlite:///blog.db"


def init_db(app: Flask) -> None:
    """初始化 SQLite 与 SQLAlchemy，并自动建库建表。"""
    app.config.setdefault("SQLALCHEMY_DATABASE_URI", SQLITE_URI)
    app.config.setdefault("SQLALCHEMY_TRACK_MODIFICATIONS", False)
    db.init_app(app)

    with app.app_context():
        # 主动建立一次连接，确保数据库文件被创建
        db.engine.connect().close()
        db.create_all()
