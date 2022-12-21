from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from app.environment import DB_URL

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = DB_URL
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)

    with app.app_context():
        from app.routes import views
        from app.models import models

        return app
