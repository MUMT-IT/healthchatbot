import os
from flask import Flask
from dotenv import load_dotenv
from rdflib import Literal
from extensions import *
from .student_reports.resources.reports import ReportTopicResource, ReportTopicListResource, ReportSubTopicListResource, \
    ReportSubTopicResource, ComplaintReportListResource

load_dotenv()
DB_URI = Literal(os.environ.get('DATABASE_URL'))

from .student_reports.models.reports import *
from .chatbot.models import *


def register_extensions(app):
    db.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(app)
    ma.init_app(app)
    mail.init_app(app)


def register_resources(app):
    api.add_resource(ReportTopicListResource, '/topics')
    api.add_resource(ReportTopicResource, '/topics/<int:topic_id>')
    api.add_resource(ReportSubTopicListResource, '/subtopics')
    api.add_resource(ReportSubTopicResource, '/subtopics/<int:subtopic_id>')
    api.add_resource(ComplaintReportListResource, '/complaints')
    api.init_app(app)


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
    app.config['MAIL_DEFAULT_SENDER'] = ('MUMT-Student Report', os.environ.get('MAIL_USERNAME'))

    register_extensions(app)
    register_resources(app)
    return app
