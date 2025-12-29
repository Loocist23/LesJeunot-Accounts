from datetime import timedelta

from flask import Flask, Response
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from werkzeug.exceptions import HTTPException

from config import settings
from database import Base, engine


def create_app() -> Flask:
    """Application factory with sane defaults and registrations."""
    app = Flask(__name__)
    app.config.update(
        SECRET_KEY=settings.secret_key,
        JWT_SECRET_KEY=settings.jwt_secret_key,
        JWT_ACCESS_TOKEN_EXPIRES=timedelta(hours=6),
        JWT_REFRESH_TOKEN_EXPIRES=timedelta(days=7),
        JWT_ENCODE_ISSUER=settings.jwt_issuer,
    )
    JWTManager(app)
    origins = [
        origin.strip()
        for origin in settings.cors_origins.split(",")
        if origin.strip()
    ]
    CORS(app, resources={r"/*": {"origins": origins or "*"}})

    Base.metadata.create_all(bind=engine)

    from routes.Index import bp as index
    from routes.v1.Tickets import bp as v1_tickets
    from routes.v1.Users import bp as v1_users

    app.register_blueprint(index, url_prefix="/")
    app.register_blueprint(v1_users, url_prefix="/v1/user")
    app.register_blueprint(v1_tickets, url_prefix="/v1/ticket")

    @app.errorhandler(401)
    def error_handler_401(error: HTTPException):
        return {
            "status": error.code,
            "error": error.name,
            "message": "Authorization token required.",
        }, 401

    @app.errorhandler(404)
    def error_handler_404(error: HTTPException):
        return {
            "status": error.code,
            "error": error.name,
            "message": "The requested URL was not found.",
        }, 404

    @app.after_request
    def after_request(response: Response):
        response.headers.update({"Content-Type": "application/json"})
        return response

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host=settings.host, port=settings.port, debug=False)
