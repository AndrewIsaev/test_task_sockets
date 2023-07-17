import json

import eventlet
import socketio

from entity import User, Room
from faker import Faker

fake = Faker()

sio = socketio.Server()
app = socketio.WSGIApp(sio)

users:dict[str,User] = {}
user_counter = 0
room_counter = 0
rooms = {}


@sio.event
def connect(sid, environ):
    global user_counter
    user_counter += 1
    user = User(id=user_counter, name=fake.name(), sid=sid)
    users[sid] = user

    sio.emit("message", to=sid, data=user.model_dump_json(exclude={"sid"}))


@sio.on("host")
def host(sid, data):
    global room_counter
    room_counter += 1
    room = Room(id=room_counter, title=fake.sentence(nb_words=2, variable_nb_words=False), host=users[sid],
                members=[])
    users[sid].room = room.title
    room.add_member(users[sid])
    rooms[room.id] = room.title
    sio.emit("message", data=room.model_dump_json())


@sio.event
def disconnect(sid):
    for user in users:
        if user.sid == sid:
            user.is_online = False


eventlet.wsgi.server(
    eventlet.listen(('', 5000)), app
)
