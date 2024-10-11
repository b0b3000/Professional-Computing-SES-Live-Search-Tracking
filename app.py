"""This module sets up and runs the Flask application."""

import os
from application import create_app

app = create_app()
app.secret_key = os.urandom(24)     # Used for session management.

if __name__ == '__main__':
    app.run(debug=True)
