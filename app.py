import logging

from flask import Flask, render_template

from config import get_config
from repositories.quran_repository import QuranRepository
from routes import main, search
from services.quran_search import QuranSearchService
from services.surah_names import SURAH_NAMES


def create_app(config: object | None = None) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config or get_config())

    app.config.from_prefixed_env("QURAN")
    app.json.ensure_ascii = False

    _configure_logging(app)
    _init_extensions(app)
    _register_blueprints(app)
    _register_error_handlers(app)
    _register_security_headers(app)
    _register_template_context(app)

    return app


def _configure_logging(app: Flask) -> None:
    logging.basicConfig(
        level=getattr(logging, app.config["LOG_LEVEL"].upper(), logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
    app.logger.setLevel(getattr(logging, app.config["LOG_LEVEL"].upper(), logging.INFO))


def _init_extensions(app: Flask) -> None:
    # The repository and search service are built once at startup and are
    # read-only afterwards, so they are safe to share across all requests.
    repository = QuranRepository(app.config["QURAN_DATA_FILE"])
    search_service = QuranSearchService(repository)
    app.extensions["quran_repository"] = repository
    app.extensions["quran_search"] = search_service


def _register_blueprints(app: Flask) -> None:
    app.register_blueprint(main)
    app.register_blueprint(search)


def _register_template_context(app: Flask) -> None:
    @app.context_processor
    def inject_surah_names():
        return {"surah_names": SURAH_NAMES}


def _register_error_handlers(app: Flask) -> None:
    @app.errorhandler(400)
    def bad_request(error):
        return render_template("error.html", code=400, message="طلب غير صالح"), 400

    @app.errorhandler(404)
    def not_found(error):
        return render_template("error.html", code=404, message="الصفحة غير موجودة"), 404

    @app.errorhandler(500)
    def internal_error(error):
        app.logger.exception("Unhandled error: %s", error)
        return render_template("error.html", code=500, message="حدث خطأ داخلي"), 500


def _register_security_headers(app: Flask) -> None:
    @app.after_request
    def set_security_headers(response):
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "no-referrer")
        response.headers.setdefault(
            "Content-Security-Policy",
            "default-src 'self'; style-src 'self' https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com; script-src 'self'",
        )
        return response


app = create_app()


if __name__ == "__main__":
    # Development launcher. Production should use gunicorn (see Dockerfile).
    app.run(host="0.0.0.0", port=5000, debug=app.config["DEBUG"])