import json
from random import choice

import discord
from discord import app_commands
from discord.ext import commands

from cogs.commands import BenPhoneResponses
from utils.error import on_app_command_error


# Context menu commands cannot be within classes
@app_commands.context_menu(name="Ben Response")
async def ben_answer(inter: discord.Interaction, message: discord.Message) -> discord.Message:
    """Get a randomised answer from Ben"""
    resp, gif = choice(tuple(BenPhoneResponses)).value
    return await inter.response.send_message(f"> [{message.author}] {message.content}\n{resp}\n{inter.client.FILE_URL}/{gif}")


class Ben(commands.AutoShardedBot):
    def __init__(self) -> None:
        with open("config.json", "r") as config:
            self.config = json.load(config)
        super().__init__(
            intents=discord.Intents.all(),
            command_prefix="ben ",
            application_id=self.config["application_id"],
            help_command=None,
            chunk_guilds_on_startup=False,
        )
        self.tree.add_command(ben_answer)
        self.calling = {}
        self.FILE_URL = "https://static.cobaltonline.net/talking-ben"

    async def setup_hook(self) -> None:
        self.on_app_command_error = self.tree.error(on_app_command_error)
        await self.load_extension("cogs.commands")
        await self.load_extension("cogs.background")
        await self.load_extension("cogs.owner")
        await self.load_extension("jishaku")

    async def on_ready(self) -> None:
        print("\U0000260e Talking Ben is ready to take calls")

    async def on_guild_leave(self, guild: discord.Guild) -> None:
        """End all calls on guild leave"""
        for chn in guild.channels:
            self.calling.pop(chn.id, None)
