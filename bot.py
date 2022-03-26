import asyncio
import json
from random import choice

import discord
from discord import app_commands
from discord.ext import commands, tasks

from cogs.commands import BenPhoneResponses


# Context menu commands cannot be within classes
@app_commands.context_menu(name="Ben Response")
async def ben_answer(inter: discord.Interaction, message: discord.Message) -> discord.Message:
    """Get a randomised answer from Ben"""
    await inter.response.defer()
    resp = choice(tuple(BenPhoneResponses))
    return await inter.followup.send(
        f"> [{message.author}] {message.content}\n{resp.value[0]}", file=discord.File(resp.value[1])
    )


class Ben(commands.AutoShardedBot):
    def __init__(self) -> None:
        with open("config.json", "r") as config:
            self.config = json.load(config)
        super().__init__(
            intents=discord.Intents.all(),
            command_prefix="ben ",
            application_id=self.config["application_id"],
            help_command=None,
        )
        self.tree.add_command(ben_answer)

    async def setup_hook(self) -> None:
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


async def boot() -> None:
    async with Ben() as bot:
        return await bot.start(bot.config.get("token"))


asyncio.run(boot())
