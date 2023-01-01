from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from backend.app.environment import AIRFLOW_DB_URL


def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = AIRFLOW_DB_URL
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db = SQLAlchemy(app)
    db.init_app(app)

    with app.app_context():
        from backend.app.routes import views
        from backend.app.models import models
        db.create_all()
        return app
