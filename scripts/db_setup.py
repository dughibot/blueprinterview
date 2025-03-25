from backend.app import app
from backend.providers.postgres import *  # import models to be created

with app.app_context():
    db.create_all()
