# app.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    uri = os.getenv("DATABASE_URL")  # HerokuのデータベースURLを取得
    if uri.startswith("postgres://"):
      uri = uri.replace("postgres://", "postgresql://", 1)
      
    app.config['SQLALCHEMY_DATABASE_URI'] = uri

    db.init_app(app)

    return app
