from flask import Flask
from resources.postgres import db
from flask_migrate import Migrate


def create_app() -> Flask:
    """Configures and creates the application server"""
    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = (
        "postgresql://postgres:password@localhost:5432/screeners_db"
    )
    # initialize db connection with the application
    db.init_app(app)
    migrate = Migrate(app, db)

    # register our endpoints
    from controllers import screener_api

    app.register_blueprint(screener_api.bp)

    return app


app = create_app()
