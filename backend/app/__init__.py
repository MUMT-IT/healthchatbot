import os
from flask import Flask
from dotenv import load_dotenv

load_dotenv()


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
    app.config['LINE_MESSAGE_API_ACCESS_TOKEN'] = os.environ.get('LINE_MESSAGE_API_ACCESS_TOKEN')
    app.config['LINE_MESSAGE_API_CLIENT_SECRET'] = os.environ.get('LINE_MESSAGE_API_CLIENT_SECRET')

    from app.chatbot import bot_bp
    app.register_blueprint(bot_bp, url_prefix='/bot')

    return app
