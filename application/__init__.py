from flask import Flask
#from dotenv import load_dotenv

def create_app():
    app = Flask(__name__)
    
    # TODO: For when we load environment variables
    #load_dotenv()

    with app.app_context():
        # Import routes
        from . import routes

    return app
