from flask import Flask
#from dotenv import load_dotenv

def create_app():
    app = Flask(__name__)
    

    with app.app_context():
        # Import routes
        from . import routes

    return app
