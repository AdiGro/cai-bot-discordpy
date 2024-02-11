from typing import Optional

from models.characters import characters
from characterai import PyAsyncCAI
from models.classes import CharInfo, MessageReponse


class CAIClient:
    def __init__(self, token):
        self.client = PyAsyncCAI(token)
        self.chat = self.client.chat

    def get_all_char_names(self):
        return [char["name"] for char in characters]

    def get_char_by_name(self, name) -> CharInfo:
        for char in characters:
            if char["name"] == name:
                return char
        raise ValueError(f"Character with name {name} not found")

    def get_char_by_id(self, char_id) -> CharInfo:
        for char in characters:
            if char["char_id"] == char_id:
                return char
        raise ValueError(f"Character with id {char_id} not found")

    def get_char_by_username(self, username) -> CharInfo:
        for char in characters:
            if char["username"] == username:
                return char

        raise ValueError(f"Character with username {username} not found")

    async def new_chat(self, char_id: str) -> str:
        res = await self.chat.new_chat(char_id)
        return res["external_id"]

    async def send_message(self, chat_id, char_username, message):
        print(chat_id, char_username, message)
        response = await self.chat.send_message(chat_id, char_username, message)
        char_info = self.get_char_by_username(char_username)
        av = char_info["avatar_url"]
        return MessageReponse(response, av, char_info["name"])
