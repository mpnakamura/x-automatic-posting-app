# app.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
from flask_migrate import Migrate


db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    uri = os.getenv("DATABASE_URL")  # HerokuのデータベースURLを取得
    if uri.startswith("postgres://"):
      uri = uri.replace("postgres://", "postgresql://", 1)
      
    app.config['SQLALCHEMY_DATABASE_URI'] = uri

    db.init_app(app)
    migrate = Migrate(app, db)

    return app
