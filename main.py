import socketio
from aiohttp import web, web_request

from entity import User, Room
from faker import Faker

fake = Faker()

sio = socketio.AsyncServer(async_mode="aiohttp")
routes = web.RouteTableDef()

users: dict[str, User] = {}
#user_counter: int = 0
#room_counter: int = 0
rooms: dict[int, Room] = {}


@sio.event
async def connect(sid: str, environ: dict) -> None:
    """
    Connect to server
    :param sid: user sid
    :param environ:
    :return: None
    """
    user_counter = len(users) + 1

    user: User = User(id=user_counter, name=fake.name(), sid=sid)
    users[sid] = user

    await sio.emit("message", to=sid, data=user.model_dump_json(exclude={"sid"}))


@sio.on("host")
async def host(sid: str, data: dict[str, str]) -> None:
    """
    Create room
    :param sid: user sid
    :param data: dict {"room_name": "room name" }
    :return: None
    """
    room_counter = len(rooms) + 1
    room: Room = Room(
        id=room_counter,
        title=fake.sentence(nb_words=2, variable_nb_words=False),
        host=users[sid],
        members=[],
    )

    users[sid].room = room.title
    room.add_member(users[sid])
    rooms[room.id] = room

    await sio.emit("message", to=sid, data=room.model_dump_json())


@sio.on("join")
async def join(sid: str, data: dict[str, int]) -> None:
    """
    Connect to room
    :param sid: user sid
    :param data: {"room_id": 1}
    :return: None
    """
    room: Room = rooms[data["room_id"]]
    user: User = users[sid]

    sio.enter_room(sid, room=room.title)
    room.add_member(users[sid])
    user.room = room.title

    await sio.emit("message", to=sid, data=room.model_dump_json())


@sio.on("leave")
async def leave(sid: str, data: dict[str, int]) -> None:
    """
    Leave room
    :param sid: user sid
    :param data: {"room_id": 1}
    :return: None
    """
    room: Room = rooms[data["room_id"]]
    user: User = users[sid]
    if user.sid != room.host.sid:
        await sio.leave_room(sid=sid, room=room)
        user.room = None
        room.remove_member(user)
    else:
        await sio.emit("message", to=sid, data={"message": "Host can`t leave the room"})


@sio.on("message/room")
async def to_room(sid: str, data: dict[str, int]) -> None:
    room: Room = rooms[data["room_id"]]
    user: User = users[sid]
    if room.host == user:
        await sio.emit("message", room=room.title, data={"message": data["message"]})


@sio.event
async def disconnect(sid: str):
    users[sid].is_online = False


@routes.get("/api/room")
async def show_rooms(request: web_request):
    """
    Show rooms
    :param request: request
    :return: Json with rooms
    """
    data: list[dict[str, dict[str, str | int]]] = []
    for room in rooms.values():
        room_data: dict[str, dict[str, str | int]] = {
            room.title: {"host": room.host.name, "members": len(room.members)}
        }
        data.append(room_data)
    return web.json_response(data=data)


app = web.Application()
sio.attach(app)
app.add_routes(routes)

if __name__ == "__main__":
    web.run_app(app)
