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
        self.bot.calling = {}

    async def test_messages(self, inter: discord.Interaction, *, scope: Literal["guild", "dm"] = "guild") -> bool:
        """Test if messages are working properly in either guild or DMs

        Args:
            inter (discord.Interaction): The command interaction to use
            scope (Literal["guild", "dm"], optional): Whether to check guild or direct messages. Defaults to "guild".

        Returns:
            bool: Returns True if messages work in the given scope
        """
        await inter.response.defer()

        if not (
            send_method := inter.followup.send
            if scope == "guild" and inter.guild
            else inter.user.send
            if scope == "dm" and inter.user
            else None
        ):
            raise app_commands.CommandError("Failed to determine send method for testing messages") from ValueError(
                "Scope must be one of 'dm', 'guild'"
            )
        try:
            await send_method(" ")
        except discord.errors.Forbidden:  # Messages not working
            return False
        except discord.errors.HTTPException:  # Messages work
            return True

    @app_commands.command(name="dmcall", description="Start a call with Ben in DMs")
    async def dmcall(self, inter: discord.Interaction) -> discord.Message:

        if self.bot.calling.get(inter.user.id):
            return await inter.response.send_message("\U0000260E There is already a call in this DM", ephemeral=True)

        if not await self.test_messages(inter, scope="dm"):
            if inter.guild and await self.test_messages(inter, scope="guild"):
                return await inter.followup.send(
                    "\U0000260E I cannot send you DMs. Please check your privacy settings.", ephemeral=True
                )
            else:
                raise app_commands.CommandError(
                    f"I cannot send messages to your DMs or in guild '{inter.guild.name}'. Please check my guild permissions or your privacy settings."
                )

        await inter.followup.send(f"\U0000260E Started a call in your DMs, {inter.user.mention}", ephemeral=True)
        await inter.user.send(
            "\U0000260E *Ben?*\nhttps://objectstorage.uk-cardiff-1.oraclecloud.com/n/axfzjalldweh/b/cobalt-static-bkt/o/talkingben-pickup.gif"
        )
        self.bot.calling[inter.user.id] = True
        while True:
            try:
                msg = await self.bot.wait_for(
                    "message", check=lambda m: isinstance(m.channel, discord.DMChannel) and m.author == inter.user, timeout=30.0
                )
            except asyncio.TimeoutError:
                self.bot.calling.pop(inter.user.id, None)
                with suppress(discord.errors.Forbidden):
                    return await inter.user.send(
                        "https://objectstorage.uk-cardiff-1.oraclecloud.com/n/axfzjalldweh/b/cobalt-static-bkt/o/talkingben-hangup.gif"
                    )

            try:
                if msg.author == self.bot.user or not self.bot.calling.get(inter.user.id):
                    break
                if randint(1, 15) == 15:
                    self.bot.calling.pop(inter.user.id, None)
                    return await msg.reply(
                        "https://objectstorage.uk-cardiff-1.oraclecloud.com/n/axfzjalldweh/b/cobalt-static-bkt/o/talkingben-hangup.gif"
                    )
                resp, gif = choice(tuple(BenPhoneResponses)).value
                await msg.reply(
                    f"{resp}\nhttps://objectstorage.uk-cardiff-1.oraclecloud.com/n/axfzjalldweh/b/cobalt-static-bkt/o/talkingben-{gif}.gif"
                )
            except discord.errors.Forbidden:
                self.bot.calling.pop(inter.user.id, None)

    @app_commands.command(name="call", description="Start a phone call with Ben in your server")
    async def call(self, inter: discord.Interaction) -> discord.Message:

        if not await self.test_messages(inter, scope="guild"):
            if await self.test_messages(inter, scope="dm"):
                return await inter.user.send(
                    f"\U0000260E I cannot send messages in guild '{inter.guild.name}' - please check my permissions",
                    ephemeral=True,
                )
            else:
                raise app_commands.CommandError(
                    f"I cannot send messages to your DMs or in guild '{inter.guild.name}'. Please check my guild permissions or your privacy settings."
                )

        if not inter.guild:
            return await inter.followup.send("\U0000260E Run the /dmcall command to start a call in DMs", ephemeral=True)

        if self.bot.calling.get(inter.channel.id):
            return await inter.followup.send("\U0000260E There is already a call in this channel", ephemeral=True)

        await inter.followup.send(
            "\U0000260E *Ben?*\nhttps://objectstorage.uk-cardiff-1.oraclecloud.com/n/axfzjalldweh/b/cobalt-static-bkt/o/talkingben-pickup.gif"
        )
        self.bot.calling[inter.channel.id] = True

        while True:
            try:
                msg = await self.bot.wait_for("message", check=lambda m: m.channel == inter.channel, timeout=30.0)
            except asyncio.TimeoutError:
                self.bot.calling.pop(inter.channel.id, None)
                return await inter.followup.send(
                    "https://objectstorage.uk-cardiff-1.oraclecloud.com/n/axfzjalldweh/b/cobalt-static-bkt/o/talkingben-hangup.gif"
                )

            try:
                if msg.author == self.bot.user or not self.bot.calling.get(inter.channel.id):
                    break
                if randint(1, 15) == 15:
                    self.bot.calling.pop(inter.channel.id, None)
                    return await msg.reply("https://objectstorage.uk-cardiff-1.oraclecloud.com/n/axfzjalldweh/b/cobalt-static-bkt/o/talkingben-hangup.gif")
                resp, gif = choice(tuple(BenPhoneResponses)).value
                await msg.reply(
                    f"{resp}\nhttps://objectstorage.uk-cardiff-1.oraclecloud.com/n/axfzjalldweh/b/cobalt-static-bkt/o/talkingben-{gif}"
                )
            except discord.errors.Forbidden:
                self.bot.calling.pop(inter.channel.id, None)

    @app_commands.command(name="end", description="End the current call")
    async def end(self, inter: discord.Interaction) -> discord.Message:
        self.bot.calling.pop(inter.channel.id if inter.guild else inter.user.id, None)
        return await inter.response.send_message(
            "https://objectstorage.uk-cardiff-1.oraclecloud.com/n/axfzjalldweh/b/cobalt-static-bkt/o/talkingben-hangup.gif"
        )

    @app_commands.command(name="drink", description="Drink some apple cider")
    async def drink(self, inter: discord.Interaction) -> discord.Message:
        return await inter.response.send_message(
            "https://objectstorage.uk-cardiff-1.oraclecloud.com/n/axfzjalldweh/b/cobalt-static-bkt/o/talkingben-drink.gif"
        )

    @app_commands.command(name="beans", description="Eat some beans")
    async def beans(self, inter: discord.Interaction) -> discord.Message:
        return await inter.response.send_message(
            "https://objectstorage.uk-cardiff-1.oraclecloud.com/n/axfzjalldweh/b/cobalt-static-bkt/o/talkingben-beans.gif"
        )

    @app_commands.command(name="burp", description="Make Ben burp")
    async def burp(self, inter: discord.Interaction) -> discord.Message:
        return await inter.response.send_message(
            "https://objectstorage.uk-cardiff-1.oraclecloud.com/n/axfzjalldweh/b/cobalt-static-bkt/o/talkingben-burp.gif"
        )

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
        return await inter.response.send_message(
            f"https://objectstorage.uk-cardiff-1.oraclecloud.com/n/axfzjalldweh/b/cobalt-static-bkt/o/talkingben-{f}"
        )

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
        return await inter.response.send_message(
            f"https://objectstorage.uk-cardiff-1.oraclecloud.com/n/axfzjalldweh/b/cobalt-static-bkt/o/talkingben-{choice(['news_fight', 'news_fight2'])}.gif"
        )

    @app_commands.command(name="punch", description="Punch Tom")
    async def punch(self, inter: discord.Interaction) -> discord.Message:
        return await inter.response.send_message(
            "https://objectstorage.uk-cardiff-1.oraclecloud.com/n/axfzjalldweh/b/cobalt-static-bkt/o/talkingben-punch.gif"
        )

    @app_commands.command(name="shoot", description="Shoot Tom with a suction dart gun")
    async def shoot(self, inter: discord.Interaction) -> discord.Message:
        return await inter.response.send_message(
            f"https://objectstorage.uk-cardiff-1.oraclecloud.com/n/axfzjalldweh/b/cobalt-static-bkt/o/talkingben-{choice['dartgun', 'dartgun_2']}.gif"
        )


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(BenCommands(bot))
