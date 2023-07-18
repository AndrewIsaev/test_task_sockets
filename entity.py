from pydantic import BaseModel


class User(BaseModel):
    """User entity"""
    id: int
    name: str
    sid: str
    room: str = None
    is_online: bool = True


class Room(BaseModel):
    """Room entity"""
    id: int
    title: str
    host: User
    members: list[User] = []

    def add_member(self, member: User) -> None:
        """
        Add user to room
        :param member: User
        :return: None
        """
        self.members.append(member)

    def remove_member(self, member: User) -> None:
        """
        Remove user from room
        :param member: User
        :return: None
        """
        self.members.remove(member)
