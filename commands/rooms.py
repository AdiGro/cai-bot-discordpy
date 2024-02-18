import discord
from discord.ext.commands import GroupCog, Cog
from discord.app_commands import Group, Transform, command

from models import ChatRoom

print(ChatRoom)
from converters import CharacterTransformer


class Room(GroupCog):
    def __init__(self, bot):
        self.bot = bot
        self.chatroom: ChatRoom = bot.cai
        self.webhooks = {}
        self.invites = {}
        self.locked = set()

    @command(name="create")
    async def create_room(
        self, interaction, char_id: Transform[str, CharacterTransformer]
    ):
        if self.chatroom.get_room(interaction.user.id):
            await interaction.response.send_message("You already have a room")
            return

        room = await self.chatroom.create_room(interaction.user, char_id=char_id)
        await interaction.response.send_message(f"Room created with {room.char_name}")

    @command(name="invite")
    async def invite(self, interaction, user: discord.Member):
        room = self.chatroom.get_room(interaction.user.id)
        if not room:
            await interaction.response.send_message("You don't have a room")
            return
        if user.id in room.participants:
            await interaction.response.send_message(
                f"{user.mention} is already in your room"
            )
            return
        if room.total_participants >= 5:
            await interaction.response.send_message(
                "You have reached the maximum number of participants"
            )
            return
        self.invites.setdefault(interaction.user.id, []).append(user.id)
        await interaction.response.send_message(f"Invited {user.mention} to your room")

    @command(name="join")
    async def join(self, interaction, owner: discord.Member):
        room = self.chatroom.get_room(owner.id)
        if not room:
            await interaction.response.send_message(f"{owner.mention} has no room")
            return
        if interaction.user.id not in self.invites.get(owner.id, []):
            await interaction.response.send_message(
                f"You are not invited to {owner.mention}'s room"
            )
            return
        if room.total_participants >= 5:
            await interaction.response.send_message(f"{owner.mention}'s room is full")
            return
        self.chatroom.join_room(owner, interaction.user)
        await interaction.response.send_message(f"Joined {owner.mention}'s room")

    @command(name="leave")
    async def leave(self, interaction):
        room = self.chatroom.get_room(interaction.user.id)
        if not room:
            await interaction.response.send_message("You are not in any room")
            return
        if room.owner_id == interaction.user.id:
            await interaction.response.send_message(
                "You are the owner of the room. Use /room disband to delete the room"
            )
            return
        (interaction.user)
        await interaction.response.send_message("Left the room")

    @command(name="disband")
    async def disband(self, interaction):
        room = self.chatroom.get_room(interaction.user.id)
        if not room:
            await interaction.response.send_message("You are not in any room")
            return
        if room.owner_id != interaction.user.id:
            await interaction.response.send_message("You are not the owner of the room")
            return
        del self.chatroom.rooms[interaction.user.id]
        for part in room.participants:
            del self.chatroom.rooms[part]
        if interaction.user.id in self.invites:
            del self.invites[interaction.user.id]
        await interaction.response.send_message("Room disbanded")

    @command(name="kick")
    async def kick(self, interaction, user: discord.Member):
        room = self.chatroom.get_room(interaction.user.id)
        if not room:
            await interaction.response.send_message("You are not in any room")
            return
        if room.owner_id != interaction.user.id:
            await interaction.response.send_message("You are not the owner of the room")
            return
        if user.id not in room.participants:
            await interaction.response.send_message(
                f"{user.mention} is not in your room"
            )
            return
        self.chatroom.leave_room(user)
        await interaction.response.send_message(f"{user.mention} has been kicked")

    def pre_process(self, text):
        return text.lstrip("~")

    @Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        if not message.content.startswith("~"):
            return
        room = self.chatroom.get_room(message.author.id)
        if not room:
            return

        if message.author.id in self.locked:
            return await message.add_reaction("⚠")
        async with message.channel.typing():
            self.locked.add(message.author.id)
    
            resp = await self.chatroom.send_message(
                message.author, message, self.pre_process
            )
    
            self.locked.remove(message.author.id)
    
            hook = self.webhooks.get(message.channel.id)
            if not hook:
                for webhook in await message.channel.webhooks():
                    if webhook.user.id == self.bot.user.id:
                        hook = webhook
                        break
                else:
                    hook = await message.channel.create_webhook(name="ChatRoom")
                self.webhooks[message.channel.id] = hook
        await hook.send(
            content=message.author.mention + "\n" + resp.text,
            username=resp.display_name,
            avatar_url=resp.avatar_url,
            allowed_mentions=discord.AllowedMentions.none(),
        )


async def setup(bot):
    await bot.add_cog(Room(bot))
