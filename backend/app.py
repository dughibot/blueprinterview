from flask import Flask, jsonify, abort
from resources.postgres import db
from flask_migrate import Migrate
from flask_cors import CORS
from werkzeug.exceptions import HTTPException


def create_app() -> Flask:
    """Configures and creates the application server"""
    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = (
        "postgresql://postgres:password@localhost:5432/screeners_db"
    )
    # initialize db connection with the application
    db.init_app(app)
    migrate = Migrate(app, db)
    CORS(app)  # Enable CORS for all routes

    # register our endpoints
    from controllers import screener_api

    app.register_blueprint(screener_api.bp)

    return app


app = create_app()


# add a bit of very basic error handling
@app.errorhandler(HTTPException)
def resource_not_found(e):
    return jsonify(error=str(e)), e.code
