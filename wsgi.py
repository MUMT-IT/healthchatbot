from app import create_app


app = create_app()


@app.route('/')
def hello():
    return 'Hello, I am up and running!'
