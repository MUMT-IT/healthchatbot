import os
from flask import Flask
from dotenv import load_dotenv
from rdflib import Literal
from extensions import db, migrate, cors

load_dotenv()
DB_URI = Literal(os.environ.get('DATABASE_URL'))

from .student_reports.models.reports import *
from .chatbot.models import *


def register_extensions(app):
    db.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(app)


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')

    register_extensions(app)
    return app
