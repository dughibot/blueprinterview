from flask import Flask
from providers.postgres import db


def create_app() -> Flask:
    """Configures and creates the application server"""
    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = (
        "postgresql://postgres:password@localhost:5432/screeners_db"
    )
    # initialize db connection with the application
    db.init_app(app)

    # register our endpoints
    from controllers import screener

    app.register_blueprint(screener.bp)

    return app


create_app()
