import discord

from discord.ext import commands
from models.chatroom import ChatRoom
import asyncio

class ChatBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cai = ChatRoom(token="<YOUR TOKEN HERE>")

    async def setup_hook(self) -> None:
        # await self.load_extension("jishaku")
        await self.load_extension("commands.rooms")

    async def on_ready(self):
        print("Ready!")

    async def close(self):
        rooms = self.cai.to_raw()  # this is a list of rooms
        # do your db logic/save rooms in db if you'd like.
        await super().close()


bot = ChatBot(
    command_prefix=commands.when_mentioned_or("!"), intents=discord.Intents.all()
)
from typing import Literal, Optional

import discord
from discord.ext import commands


@bot.command()
@commands.guild_only()
@commands.is_owner()
async def sync(
    ctx: commands.Context,
    guilds: commands.Greedy[discord.Object],
    spec: Optional[Literal["~", "*", "^"]] = None,
) -> None:
    if not guilds:
        if spec == "~":
            synced = await ctx.bot.tree.sync(guild=ctx.guild)
        elif spec == "*":
            ctx.bot.tree.copy_global_to(guild=ctx.guild)
            synced = await ctx.bot.tree.sync(guild=ctx.guild)
        elif spec == "^":
            ctx.bot.tree.clear_commands(guild=ctx.guild)
            await ctx.bot.tree.sync(guild=ctx.guild)
            synced = []
        else:
            synced = await ctx.bot.tree.sync()

        await ctx.send(
            f"Synced {len(synced)} commands {'globally' if spec is None else 'to the current guild.'}"
        )
        return

    ret = 0
    for guild in guilds:
        try:
            await ctx.bot.tree.sync(guild=guild)
        except discord.HTTPException:
            pass
        else:
            ret += 1

    await ctx.send(f"Synced the tree to {ret}/{len(guilds)}.")


bot.run("<YOUR BOT TOKEN HERE>")
