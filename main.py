# Importing Modules
from flask import Flask, render_template, redirect, request, jsonify, session
from flask_socketio import SocketIO, emit
from flask_sqlalchemy import SQLAlchemy
import json
import os

# Getting variable Configurations
with open("config.json") as f:
    data = json.load(f)

# Creating App
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
    finished = db.Column(db.Boolean, nullable=False)
    joined = db.Column(db.Boolean, nullable=False)

    def __init__(self, first):
        self.first = first
        self.second = None
        self.status = "n" * 9
        self.turn = first
        self.finished = False
        self.joined = False


# Players Table
class Players(db.Model):
    __tablename__ = "players"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(10), nullable=False)

    def __init__(self, name):
        self.name = name


# Main Route
@app.route('/')
def home():
    if "player" in session:
        room_f__ = db.session.query(Rooms).filter(Rooms.first == session["player"]).first()
        room_s__ = db.session.query(Rooms).filter(Rooms.second == session["player"]).first()
        if room_f__ is not None:
            return redirect(f"/{room_f__.id}")
        elif room_s__ is not None:
            return redirect(f"/{room_s__.id}")
        else:
            session.pop('player')
    return render_template("index.html")


@app.route('/create_room', methods=["POST"])
def create_room():
    # Creating new room
    if request.method == "POST":
        if "player" not in session:
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
            except:
                return jsonify(error="Some error occurred")
        return jsonify(error="You can join only one game at a time")


@app.route('/join_room', methods=["POST"])
def join_room():
    # Joining a room
    if request.method == "POST":
        if "player" not in session:
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
            except:
                return jsonify(error="Some error occurred")
        return jsonify(error="You can join only one game at a time")


@app.route('/<int:roomID>')
def game(roomID):
    # Game route
    room = db.session.query(Rooms).filter(Rooms.id == roomID).first()
    if room is not None:
        if "player" in session:
            player__ = session["player"]
            if room.first == player__ or room.second == player__:
                boxes__ = [room.status[i] for i in range(9)]
                my_turn = False
                is_owner = False
                if room.turn == player__:
                    my_turn = True
                if room.first == player__:
                    is_owner = True
                return render_template("game.html", boxes=boxes__, my_turn=my_turn, player=player__, owner=is_owner)
    return redirect('/')


def gameLogic(status):
    # Logic of winning or draw
    win_positions = [[0, 1, 2], [3, 4, 5], [6, 7, 8],
                     [0, 3, 6], [1, 4, 7], [2, 5, 8],
                     [0, 4, 8], [2, 4, 6]]
    for item in win_positions:
        if status[item[0]] == status[item[1]] and status[item[1]] == status[item[2]]:
            if status[item[0]] == "X":
                return [True, 1]
            if status[item[0]] == "O":
                return [True, 2]
    if "n" in status:
        return [False, -1]
    return [True, 0]


@socket.on('clickBox')
def clickBox(id__, ind__):
    # Clicking a box
    room_id__ = int(id__)
    room__ = db.session.query(Rooms).filter(Rooms.id == room_id__).first()
    if "player" in session:
        # Getting data
        player__ = session["player"]
        clicked_ind__ = int(ind__)

        if room__.first == player__ or room__.second == player__:
            room_obj__ = db.session.query(Rooms).filter(Rooms.id == room_id__)
            if not room__.finished:
                if room__.turn == player__:
                    if room__.status[clicked_ind__] == "n":
                        if player__ == room__.first:
                            change_status = "X"
                            change_turn = room__.second if room__.second is not None else -1
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
                        won__, who_won__ = gameLogic(room__.status)
                        if won__:
                            if who_won__ == 1:
                                who_won__ = room__.first
                            elif who_won__ == 2:
                                who_won__ = room__.second
                            room_obj__.update({Rooms.finished: True})
                            db.session.commit()
                            emit('click_result',
                                 {"result": room__.status, "success": who_won__, "error": None,
                                  "turn": room__.turn, "roomID": id__},
                                 broadcast=True)
                        else:
                            emit('click_result',
                                 {"result": room__.status, "success": None, "error": None, "turn": room__.turn, "roomID": id__},
                                 broadcast=True)
                        return
                    emit('click_result',
                         {"result": None, "success": None, "error": "Click on empty box", "errorID": player__, "roomID": id__},
                         broadcast=True)
                    return
                emit('click_result',
                     {"result": None, "success": None, "error": "Click when your turn comes", "errorID": player__, "roomID": id__},
                     broadcast=True)
                return
            emit('click_result',
                 {"result": None, "success": None, "error": "Game is overed. Restart to play again.",
                  "errorID": player__, "roomID": id__},
                 broadcast=True)
            return
    emit('click_result', {"result": None, "success": None, "error": "You are not present in room", "roomID": id__},
         broadcast=True)
    return


@socket.on('dltRoom')
def dltRoom(id__):
    # Deleting Room
    room_id__ = int(id__)
    room__ = db.session.query(Rooms).filter(Rooms.id == room_id__).first()
    first__ = db.session.query(Players).filter(Players.id == room__.first).first()
    second__ = db.session.query(Players).filter(Players.id == room__.second).first()
    db.session.delete(first__)
    if second__ is not None:
        db.session.delete(second__)
    db.session.delete(room__)
    db.session.commit()
    session.pop("player")
    emit('room_deleted', {"roomID": id__}, broadcast=True)


@socket.on('restartGame')
def restartGame(id__):
    # Restarting Game
    room_id__ = int(id__)
    room__ = db.session.query(Rooms).filter(Rooms.id == room_id__)
    room__.update({Rooms.status: "n" * 9, Rooms.turn: room__.first().first,
                   Rooms.finished: False})
    db.session.commit()
    emit('game_restarted', {"roomID": id__}, broadcast=True)


@socket.on('quitRoom')
def quitRoom(id__):
    # Quitting Room
    room_id__ = int(id__)
    room__ = db.session.query(Rooms).filter(Rooms.id == room_id__)
    second__ = db.session.query(Players).filter(Players.id == room__.first().second).first()
    room__.update({Rooms.status: "n" * 9, Rooms.turn: room__.first().first,
                   Rooms.finished: False, Rooms.second: None, Rooms.joined: False})
    second_id__ = second__.id
    second_name__ = second__.name
    db.session.delete(second__)
    db.session.commit()
    session.pop("player")
    emit('room_exited', {"msg": f"{second_name__} Left", "id": second_id__, "roomID": id__}, broadcast=True)


@socket.on('joinedRoom')
def joinedRoom(id__, player__):
    # Joining Room Message Flash
    room_id__ = int(id__)
    room__ = db.session.query(Rooms).filter(Rooms.id == room_id__)
    first__ = db.session.query(Players).filter(Players.id == room__.first().first).first()
    if room__.first().joined or int(player__) == first__.id or room__.first().second is None:
        emit('join_msg', {"msg": None, "roomID": id__}, broadcast=True)
    else:
        second__ = db.session.query(Players).filter(Players.id == room__.first().second).first()
        room__.update({Rooms.joined: True})
        db.session.commit()
        emit('join_msg', {"msg": f"{second__.name} Joined", "roomID": id__}, broadcast=True)

if __name__ == '__main__':
    socket.run(app, debug=data["debug"], port=33507)
