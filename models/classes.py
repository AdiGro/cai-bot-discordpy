from __future__ import annotations

from dataclasses import dataclass, field
from typing import TypedDict


@dataclass
class Room:
    owner_id: int
    char_info: CharInfo
    chat_id: str
    participants: list[int] = field(default_factory=list)

    def add_participant(self, participant):
        self.participants.append(participant)

    def remove_participant(self, participant):
        self.participants.remove(participant)

    @property
    def total_participants(self):
        return len(self.participants)

    @property
    def char_id(self):
        return self.char_info["char_id"]

    @property
    def username(self):
        return self.char_info["username"]

    @property
    def char_name(self):
        return self.char_info["name"]

    @property
    def display_name(self):
        return self.char_name


class CharInfo(TypedDict):
    name: str
    char_id: str
    username: str
    avatar_url: str


@dataclass
class MessageReponse:
    """Dataclass for message response from c.ai"""

    name: str
    text: str
    reply: str
    avatar_url: str
    display_name: str

    def __init__(self, response: dict, avatar_url, display_name):
        text = response["replies"][0]["text"]
        name = response["src_char"]["participant"]["name"]
        self.text = text
        self.name = name
        self.reply = text
        self.avatar_url = avatar_url
        self.display_name = display_name

        # super().__init__(name, text, text, avatar_url, display_name)
