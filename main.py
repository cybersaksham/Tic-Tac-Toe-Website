from flask import Flask, render_template, redirect, request, jsonify
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


@app.route('/create_room', methods=["POST"])
def create_room():
    if request.method == "POST":
        try:
            # Getting data from form
            name__ = request.form["name"]

            # Making Player
            player = Players(name__)
            db.session.add(player)
            db.session.commit()

            # Making Room
            room = Rooms(player.id)
            db.session.add(room)
            db.session.commit()

            return jsonify(error=None, id=room.id)
        except Exception as e:
            return jsonify(error=str(e))


@app.route('/<int:roomID>')
def game(roomID):
    room = db.session.query(Rooms).filter(Rooms.id == roomID).first()
    if room is not None:
        boxes__ = [room.status[i] for i in range(9)]
        return render_template("game.html", boxes=boxes__)
    return redirect('/')


if __name__ == '__main__':
    socket.run(app, debug=data["debug"])
