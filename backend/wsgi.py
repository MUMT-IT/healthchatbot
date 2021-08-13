from app import create_app

app = create_app()

from app.chatbot import bot_bp
app.register_blueprint(bot_bp, url_prefix='/bot')

from app.student_reports import student_blueprint
app.register_blueprint(student_blueprint, url_prefix='/student_report')


@app.route('/')
def hello():
    return 'Hello, I am up and running!'
