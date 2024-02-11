from typing import Callable, Optional

import discord
from models.caiclient import CAIClient
from models.classes import CharInfo, Room, MessageReponse


class ChatRoom:
    def __init__(self, token=None, client: CAIClient = None):
        if not token and not client:
            raise ValueError("Either token or client must be provided")

        if not client:
            client = CAIClient(token)

        self.client = client

        self.rooms = {}

    def _create_room(self, owner_id, char: CharInfo, chat_id):
        return Room(owner_id, char, chat_id)

    async def create_room(
        self,
        owner: discord.User,
        char_id=None,
        char_name=None,
    ):
        owner_id = owner.id
        if not char_id and not char_name:
            raise ValueError("Either char_id or char_name must be provided")

        if char_id:
            char = self.client.get_char_by_id(char_id)
        else:
            char = self.client.get_char_by_name(char_name)

        chat_id = await self.client.new_chat(char["char_id"])
        room = self._create_room(owner_id, char, chat_id)
        self.rooms[owner_id] = room
        return room

    def get_room(self, user_id) -> Optional[Room]:
        return self.rooms.get(user_id)

    def join_room(self, owner: discord.User, user: discord.User):
        owner_id = owner.id
        user_id = user.id
        room = self.get_room(owner_id)
        if not room:
            raise ValueError(f"{owner.mention} has no room.")
        room.add_participant(user_id)
        self.rooms[user_id] = room

    def leave_room(self, user: discord.User):
        user_id = user.id
        room = self.get_room(user_id)
        if not room:
            raise ValueError(f"{user.mention} is not in any room")
        room.remove_participant(user_id)
        del self.rooms[user_id]

    def process_message(self, user: discord.User, message: discord.Message, text: str):
        # replace all mentions with the name of the user
        for mention in message.mentions:
            text = text.replace(mention.mention, mention.name)
        return f"{user.name}: {text}"

    async def send_message(
        self,
        user: discord.User,
        message: discord.Message,
        pre_process: Optional[Callable[[str], str]],
    ) -> MessageReponse:
        user_id = user.id
        text_msg = message.content
        if pre_process:
            text_msg = pre_process(text_msg)
        text = self.process_message(user, message, text_msg)
        room = self.get_room(user_id)
        if not room:
            raise ValueError(f"{user.mention} is not in any room")

        chat_id = room.chat_id
        username = room.username

        return await self.client.send_message(chat_id, username, text)

    @classmethod
    def from_raw(cls, token, rooms):
        chat_room = cls(token)
        rooms_cls = {}
        for room in rooms:
            owner_id = room["owner_id"]
            user_id = room["user_id"]
            char_info: CharInfo = room["char_info"]
            chat_id = room["chat_id"]
            rooms_cls[user_id] = chat_room._create_room(owner_id, char_info, chat_id)

        chat_room.rooms = rooms_cls
        return chat_room

    def to_raw(self):
        return [
            {
                "user_id": user_id,
                "owner_id": room.owner_id,
                "char_info": room.char_info,
                "chat_id": room.chat_id,
            }
            for user_id, room in self.rooms.items()
        ]
