from flask import Flask, render_template, redirect, request, jsonify, session
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

            # Adding to session storage
            session["player"] = player.id

            # Making Room
            room = Rooms(player.id)
            db.session.add(room)
            db.session.commit()

            return jsonify(error=None, id=room.id)
        except Exception as e:
            return jsonify(error=str(e))


@app.route('/join_room', methods=["POST"])
def join_room():
    if request.method == "POST":
        try:
            # Getting data from form
            name__ = request.form["name"]
            room__ = request.form["roomID"]

            room = db.session.query(Rooms).filter(Rooms.id == room__)
            if room.first() is not None:
                if room.first().second is None:
                    # Making Player
                    player = Players(name__)
                    db.session.add(player)
                    db.session.commit()

                    # Adding to session storage
                    session["player"] = player.id

                    # Making Room
                    room.update({Rooms.second: player.id,
                                 Rooms.turn: player.id if room.first().turn == -1 else room.first().turn})
                    db.session.commit()

                    return jsonify(error=None, id=room.first().id)
                return jsonify(error="Room is full")
            return jsonify(error="No room exist")
        except Exception as e:
            return jsonify(error=str(e))


@app.route('/<int:roomID>')
def game(roomID):
    room = db.session.query(Rooms).filter(Rooms.id == roomID).first()
    if room is not None:
        if "player" in session:
            player__ = session["player"]
            if room.first == player__ or room.second == player__:
                boxes__ = [room.status[i] for i in range(9)]
                my_turn = False
                if room.turn == player__:
                    my_turn = True
                return render_template("game.html", boxes=boxes__, my_turn=my_turn)
    return redirect('/')


@app.route('/clickBox', methods=["POST"])
def clickBox():
    if request.method == "POST":
        if "player" in session:
            # Getting data
            player__ = session["player"]
            room_id__ = int(request.args.get("room"))
            clicked_ind__ = int(request.args.get("index"))

            room__ = db.session.query(Rooms).filter(Rooms.id == room_id__).first()
            room_obj__ = db.session.query(Rooms).filter(Rooms.id == room_id__)
            if room__.first == player__ or room__.second == player__:
                if room__.turn == player__:
                    if room__.status[clicked_ind__] == "n":
                        if player__ == room__.first:
                            change_status = "X"
                            change_turn = room__.second
                        else:
                            change_status = "O"
                            change_turn = room__.first
                        fin_status = ""
                        for i in range(9):
                            if i == clicked_ind__:
                                fin_status += change_status
                            else:
                                fin_status += room__.status[i]
                        room_obj__.update({Rooms.status: fin_status,
                                           Rooms.turn: change_turn})
                        db.session.commit()
                        return jsonify(error=None)
                    return jsonify(error="Cannot Click")
                return jsonify(error="Not your turn")
        return jsonify(error="Not in room")


if __name__ == '__main__':
    socket.run(app, debug=data["debug"])
