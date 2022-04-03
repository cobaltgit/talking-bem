import asyncio
from contextlib import suppress
from enum import Enum
from random import choice, randint
from typing import Literal

import discord
from discord import app_commands
from discord.ext import commands


class BenPhoneResponses(Enum):
    """Randomised phone responses in ["answer", "gif path"] format"""

    yes = ["\U0000260E *Yes?*", "yes.gif"]
    no = ["\U0000260E *No.*", "no.gif"]
    ugh = ["\U0000260E *Ugh.*", "ugh.gif"]
    hohoho = ["\U0000260E *Ho ho ho...*", "hohoho.gif"]


class BenCommands(commands.Cog, name="Commands"):
    """Commands for Talking Ben"""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="dmcall", description="Start a call with Ben in DMs")
    async def dmcall(self, inter: discord.Interaction) -> discord.Message:

        if self.bot.calling.get(inter.user.id):
            return await inter.response.send_message("\U0000260E There is already a call in this DM", ephemeral=True)

        await inter.response.defer()
        await inter.followup.send(f"\U0000260E Started a call in your DMs, {inter.user.mention}", ephemeral=True)
        self.bot.calling[inter.user.id] = True
        await inter.user.send(f"\U0000260E *Ben?*\n{self.bot.FILE_URL}/pickup.gif")
        while True:
            try:
                msg = await self.bot.wait_for(
                    "message",
                    check=lambda m: m.author != self.bot.user,
                    timeout=20,
                )
            except asyncio.TimeoutError:
                self.bot.calling.pop(inter.user.id, None)
                return await inter.followup.send(f"{self.bot.FILE_URL}/hangup.gif")

            resp, gif = choice(tuple(BenPhoneResponses)).value

            if self.bot.calling.get(inter.user.id):
                if randint(1, 15) == 15:
                    self.bot.calling.pop(inter.user.id, None)
                    return await inter.followup.send(f"{self.bot.FILE_URL}/hangup.gif")
                await msg.reply(f"{resp}\n{self.bot.FILE_URL}/{gif}")
            else:
                break

    @app_commands.command(name="call", description="Start a phone call with Ben in your server")
    async def call(self, inter: discord.Interaction) -> discord.Message:
        if not inter.guild:
            return await inter.response.send_message(
                "\U0000260E Run the /dmcall command to start a call in DMs", ephemeral=True
            )
        elif self.bot.calling.get(inter.channel.id):
            return await inter.response.send_message("\U0000260E There is already a call in this channel", ephemeral=True)

        await inter.response.defer()
        self.bot.calling[inter.channel.id] = True
        await inter.followup.send(f"\U0000260E *Ben?*\n{self.bot.FILE_URL}/pickup.gif")
        while True:
            try:
                msg = await self.bot.wait_for(
                    "message",
                    check=lambda m: m.channel == inter.channel and m.author != self.bot.user,
                    timeout=20,
                )
            except asyncio.TimeoutError:
                self.bot.calling.pop(inter.channel.id, None)
                return await inter.followup.send(f"{self.bot.FILE_URL}/hangup.gif")

            resp, gif = choice(tuple(BenPhoneResponses)).value

            if self.bot.calling.get(inter.channel.id):
                if randint(1, 15) == 15:
                    self.bot.calling.pop(inter.channel.id, None)
                    return await inter.followup.send(f"{self.bot.FILE_URL}/hangup.gif")
                await msg.reply(f"{resp}\n{self.bot.FILE_URL}/{gif}")
            else:
                break

    @app_commands.command(name="end", description="End the current call")
    async def end(self, inter: discord.Interaction) -> discord.Message:
        return (
            await inter.response.send_message(f"{self.bot.FILE_URL}/hangup.gif")
            if self.bot.calling.pop(
                inter.channel.id if inter.guild else inter.user.id, None
            )
            else await inter.response.send_message(
                "\U0000260E There is no calls currently ongoing in this channel."
            )
        )

    @app_commands.command(name="drink", description="Drink some apple cider")
    async def drink(self, inter: discord.Interaction) -> discord.Message:
        return await inter.response.send_message(f"{self.bot.FILE_URL}/drink.gif")

    @app_commands.command(name="beans", description="Eat some beans")
    async def beans(self, inter: discord.Interaction) -> discord.Message:
        return await inter.response.send_message(f"{self.bot.FILE_URL}/beans.gif")

    @app_commands.command(name="burp", description="Make Ben burp")
    async def burp(self, inter: discord.Interaction) -> discord.Message:
        return await inter.response.send_message(f"{self.bot.FILE_URL}/burp.gif")

    @app_commands.command(name="experiment", description="Experiment with different potion combinations!")
    @app_commands.describe(first_colour="The first colour to use")
    @app_commands.describe(second_colour="The second colour to use")
    @app_commands.choices(
        first_colour=[
            app_commands.Choice(name="Yellow", value=1),
            app_commands.Choice(name="Green", value=2),
            app_commands.Choice(name="Cyan", value=3),
            app_commands.Choice(name="Purple", value=4),
            app_commands.Choice(name="Blue", value=5),
        ],
        second_colour=[
            app_commands.Choice(name="Yellow", value=1),
            app_commands.Choice(name="Green", value=2),
            app_commands.Choice(name="Cyan", value=3),
            app_commands.Choice(name="Purple", value=4),
            app_commands.Choice(name="Blue", value=5),
        ],
    )
    async def experiment(
        self, inter: discord.Interaction, first_colour: app_commands.Choice[int], second_colour: app_commands.Choice[int]
    ) -> discord.Message:
        match (first_colour.name.lower(), second_colour.name.lower()):
            case ("yellow", "green") | ("green", "yellow"):
                f = "yellowgreen.gif"
            case ("yellow", "purple") | ("purple", "yellow"):
                f = "yellowpurple.gif"
            case ("yellow", "cyan") | ("cyan", "yellow"):
                f = "yellowcyan.gif"
            case ("yellow", "blue") | ("blue", "yellow"):
                f = "yellowblue.gif"
            case ("green", "purple") | ("purple", "green"):
                f = "greenpurple.gif"
            case ("green", "blue") | ("blue", "green"):
                f = "greenblue.gif"
            case ("green", "cyan") | ("cyan", "green"):
                f = "greencyan.gif"
            case ("purple", "blue") | ("blue", "purple"):
                f = "purpleblue.gif"
            case ("purple", "cyan") | ("cyan", "purple"):
                f = "cyanpurple.gif"
            case ("blue", "cyan") | ("cyan", "blue"):
                f = "cyanblue.gif"
            case (_, _):
                return await inter.response.send_message(
                    "Invalid colour choices - must be one of 'purple', 'cyan', 'blue', 'green', 'yellow', must not be equal to each other",
                    ephemeral=True,
                )
        return await inter.response.send_message(f"{self.bot.FILE_URL}/{f}")

    @app_commands.command(name="repeat", description="Ben will repeat what you say")
    @app_commands.describe(speech="What would you like Ben to say?")
    async def repeat(self, inter: discord.Interaction, *, speech: str) -> discord.Message:
        return await inter.response.send_message(speech)

    @app_commands.command(name="discord", description="Get an invite to the bot's support server")
    async def discord_invite(self, inter: discord.Interaction) -> discord.Message:
        return await inter.response.send_message(
            f"https://discord.gg/{dsc}" if (dsc := self.bot.config.get("support_discord")) else "No support server invite found"
        )

    @app_commands.command(name="fight", description="Fight Tom")
    async def fight(self, inter: discord.Interaction) -> discord.Message:
        return await inter.response.send_message(f"{self.bot.FILE_URL}/{choice(['news_fight', 'news_fight2'])}.gif")

    @app_commands.command(name="punch", description="Punch Tom")
    async def punch(self, inter: discord.Interaction) -> discord.Message:
        return await inter.response.send_message(f"{self.bot.FILE_URL}/punch.gif")

    @app_commands.command(name="shoot", description="Shoot Tom with a suction dart gun")
    async def shoot(self, inter: discord.Interaction) -> discord.Message:
        return await inter.response.send_message(f"{self.bot.FILE_URL}/{choice(['dartgun', 'dartgun_2'])}.gif")

    @app_commands.command(name="chair", description="Make Tom or Ben fall off their chair!")
    @app_commands.choices(
        who=[
            app_commands.Choice(name="Tom", value=1),
            app_commands.Choice(name="Ben", value=2),
        ]
    )
    @app_commands.describe(who="Who should fall off?")
    async def chair(self, inter: discord.Interaction, who: app_commands.Choice[int]):
        return await inter.response.send_message(f"{self.bot.FILE_URL}/chair_{who.name.lower()}.gif")


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(BenCommands(bot))
