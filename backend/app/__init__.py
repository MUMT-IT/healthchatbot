import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from dotenv import load_dotenv
from rdflib import Literal

load_dotenv()
DB_URI = Literal(os.environ.get('DATABASE_URL'))

db = SQLAlchemy()
migrate = Migrate()


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
    app.config['LINE_MESSAGE_API_ACCESS_TOKEN'] = os.environ.get('LINE_MESSAGE_API_ACCESS_TOKEN')
    app.config['LINE_MESSAGE_API_CLIENT_SECRET'] = os.environ.get('LINE_MESSAGE_API_CLIENT_SECRET')
    db.init_app(app)
    migrate.init_app(app, db)

    return app
