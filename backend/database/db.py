from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# 全局数据库实例，供模型和应用共享
db = SQLAlchemy()


def init_db(app: Flask) -> None:
    """初始化数据库并创建已注册模型对应的数据表。"""
    db.init_app(app)

    with app.app_context():
        # 统一导入模型，确保映射注册完成
        import models  # noqa: F401

        db.create_all()
