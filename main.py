from flask import Flask, render_template
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


# Rooms Table
class Rooms(db.Model):
    __tablename__ = "rooms"
    id = db.Column(db.Integer, primary_key=True)
    first = db.Column(db.Integer, nullable=False)
    second = db.Column(db.Integer)
    status = db.Column(db.String(10), nullable=False)
    turn = db.Column(db.Integer, nullable=False)

    def __init__(self, first):
        self.first = first
        self.second = None
        self.status = "n" * 9
        self.turn = first


# Players Table
class Players(db.Model):
    __tablename__ = "players"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(10), nullable=False)

    def __init__(self, name):
        self.name = name


@app.route('/')
def home():
    return render_template("index.html")


if __name__ == '__main__':
    socket.run(app, debug=data["debug"])
