"""Music Analytics API - Flask Application."""

from flask import Flask
from flask_session import Session
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
Session(app)

from routes import *

if __name__ == '__main__':
    app.run(debug=True)
