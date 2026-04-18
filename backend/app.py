import os

from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix

from database.db import init_db
from routes.blog import blog_bp
from routes.program import program_bp


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["JSON_AS_ASCII"] = False
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1)  # type: ignore[assignment]
    init_db(app)
    app.register_blueprint(program_bp, url_prefix="/api")
    app.register_blueprint(blog_bp, url_prefix="/api")
    return app


if __name__ == "__main__":
    host = os.getenv("APP_HOST", "0.0.0.0")
    port = int(os.getenv("APP_PORT", "5000"))
    debug = os.getenv("APP_DEBUG", "1").lower() in {"1", "true", "yes", "on"}
    create_app().run(host=host, port=port, debug=debug)
