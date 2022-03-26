import asyncio
from contextlib import suppress
from enum import Enum
from random import choice, randint

import discord
from discord import app_commands
from discord.ext import commands


class BenPhoneResponses(Enum):
    """Randomised phone responses in ["answer", "gif path"] format"""

    yes = ["\U0000260E *Yes?*", "files/yes.gif"]
    no = ["\U0000260E *No.*", "files/no.gif"]
    ugh = ["\U0000260E *Ugh.*", "files/ugh.gif"]
    hohoho = ["\U0000260E *Ho ho ho...*", "files/hohoho.gif"]


class BenCommands(commands.Cog, name="Commands"):
    """Commands for Talking Ben"""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.bot.calling = {}

    @app_commands.command(name="dmcall", description="Start a call with Ben in DMs")
    async def dmcall(self, inter: discord.Interaction) -> discord.Message:
        await inter.response.send_message(f"\U0000260E Started a call in your DMs, {inter.user.mention}", ephemeral=True)
        await inter.user.send("\U0000260E *Ben?*", file=discord.File("files/pickup.gif"))
        while True:
            try:
                msg = await self.bot.wait_for(
                    "message", check=lambda m: isinstance(m.channel, discord.DMChannel) and m.author == inter.user, timeout=30.0
                )
            except asyncio.TimeoutError:
                with suppress(discord.errors.Forbidden):
                    return await inter.user.send(file=discord.File("files/hangup.gif"))

            with suppress(discord.errors.Forbidden):
                if msg.author != self.bot.user:
                    if msg.content in ("stop", "goodbye", "bye") or randint(1, 15) == 15:
                        return await msg.reply(file=discord.File("files/hangup.gif"))
                    resp = choice(tuple(BenPhoneResponses))
                    await msg.reply(resp.value[0], file=discord.File(resp.value[1]))

    @app_commands.command(name="call", description="Start a phone call with Ben in your server")
    async def call(self, inter: discord.Interaction) -> discord.Message:
        if not inter.guild:
            return await inter.response.send_message(
                "\U0000260E Run the /dmcall command to start a call in DMs", ephemeral=True
            )

        if self.bot.calling.get(inter.channel.id):
            return await inter.response.send_message("\U0000260E There is already a call in this channel", ephemeral=True)

        await inter.response.defer()
        await inter.followup.send("\U0000260E *Ben?*", file=discord.File("files/pickup.gif"))
        self.bot.calling[inter.channel.id] = True

        while True:
            try:
                msg = await self.bot.wait_for("message", check=lambda m: m.channel == inter.channel, timeout=30.0)
            except asyncio.TimeoutError:
                with suppress(discord.errors.Forbidden):
                    self.bot.calling.pop(inter.channel.id, None)
                    return await inter.followup.send(file=discord.File("files/hangup.gif"))

            try:
                if msg.author != self.bot.user:
                    if msg.content.lower() in ("stop", "goodbye", "bye") or randint(1, 15) == 15:
                        self.bot.calling.pop(inter.channel.id, None)
                        return await msg.reply(file=discord.File("files/hangup.gif"))
                    resp = choice(tuple(BenPhoneResponses))
                    await msg.reply(resp.value[0], file=discord.File(resp.value[1]))
            except discord.errors.Forbidden:
                self.bot.calling.pop(inter.channel.id, None)

    @app_commands.command(name="drink", description="Drink some apple cider")
    async def drink(self, inter: discord.Interaction) -> discord.Message:
        await inter.response.defer()
        await inter.followup.send(file=discord.File("files/drink.gif"))

    @app_commands.command(name="beans", description="Eat some beans")
    async def beans(self, inter: discord.Interaction) -> discord.Message:
        await inter.response.defer()
        await inter.followup.send(file=discord.File("files/beans.gif"))

    @app_commands.command(name="burp", description="Make Ben burp")
    async def burp(self, inter: discord.Interaction) -> discord.Message:
        await inter.response.defer()
        await inter.followup.send(file=discord.File("files/burp.gif"))


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(BenCommands(bot))
