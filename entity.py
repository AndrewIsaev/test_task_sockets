from pydantic import BaseModel


class User(BaseModel):
    id: int
    name: str
    sid: str
    room: str = None
    is_online: bool = True


class Room(BaseModel):
    id: int
    title: str
    host: User
    members: list[User] = []

    def add_member(self, member):
        self.members.append(member)

    def remove_member(self, member):
        self.members.remove(member)
