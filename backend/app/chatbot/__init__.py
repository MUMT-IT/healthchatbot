from flask import Blueprint

bot_bp = Blueprint('bot', __name__)

from . import views
