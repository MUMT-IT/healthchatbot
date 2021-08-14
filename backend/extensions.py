from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_restful import Api
from flask_marshmallow import Marshmallow
from flask_mail import Mail

db = SQLAlchemy()
migrate = Migrate()
cors = CORS()
api = Api()
ma = Marshmallow()
mail = Mail()