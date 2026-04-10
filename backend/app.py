from flask import Flask

from routes.program import program_bp


def create_app() -> Flask:
    app = Flask(__name__)
    app.register_blueprint(program_bp, url_prefix="/api")
    return app


if __name__ == "__main__":
    create_app().run(host="0.0.0.0", port=5000, debug=True)
