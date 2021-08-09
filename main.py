from flask import Flask
from flask_socketio import SocketIO, emit
from flask_sqlalchemy import SQLAlchemy
import json
import os

with open("config.json") as f:
    data = json.load(f)

app = Flask(__name__)
if data["debug"]:
    app.secret_key = data["local_secret"]
    app.config['SQLALCHEMY_DATABASE_URI'] = data["local_database"]
else:
    app.secret_key = os.environ.get('SECRET_KEY', None)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', None). \
                                                replace("postgres", "postgresql") + "?sslmode=require"
db = SQLAlchemy(app)
socket = SocketIO(app)


@app.route('/')
def home():
    return "Website content"


if __name__ == '__main__':
    socket.run(app, debug=data["debug"])
