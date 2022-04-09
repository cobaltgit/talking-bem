import asyncio
import contextlib
from enum import Enum
from itertools import chain
from random import choice, randint
from PIL import UnidentifiedImageError

import discord
from discord import app_commands
from discord.ext import commands
from utils.functions import generate_news
from functools import partial
from io import BytesIO
import aiohttp


def channel_whitelisted():
    def predicate(inter: discord.Interaction) -> bool:
        gid = getattr(inter, "guild.id", None)
        if inter.channel.id in inter.client.blacklist.get(gid, []):
            raise app_commands.CheckFailure("\U0000260E This channel is blacklisted for calls")
        return True

    return app_commands.check(predicate)


class BenPhoneResponses(Enum):
    """Randomised phone responses in ["answer", "gif path"] format"""

    yes = ["\U0000260E *Yes?*", "yes.gif"]
    no = ["\U0000260E *No.*", "no.gif"]
    ugh = ["\U0000260E *Ugh.*", "ugh.gif"]
    hohoho = ["\U0000260E *Ho ho ho...*", "hohoho.gif"]


class BenNewspaperResponses(Enum):
    """Randomised newspaper responses in ["answer", "gif path"] format"""

    taunt = ["\U0001f4f0 *Na-na-na-na.*", "newspaper_taunt.gif"]
    putdown = ["\U0001f4f0 *puts newspaper down*", "newspaper_putdown.gif"]
    look = ["\U0001f4f0 ...", "newspaper_look.gif"]
    shh = ["\U0001f4f0 *Shh...*", "newspaper_shh.gif"]
    hohoho = ["\U0001f4f0 *Ho ho ho...*", "newspaper_static.png"]
    hehehe = ["\U0001f4f0 *Hehehe...*", "newspaper_static.png"]
    hm = ["\U0001f4f0 *H-h-hm...*", "newspaper_static.png"]
    mhm = ["\U0001f4f0 *Mm-hm...*", "newspaper_static.png"]
    hmhm = ["\U0001f4f0 *Hm-hm...*", "newspaper_static.png"]
    sleep = ["\U0001f4f0 \U0001f4a4...", "newspaper_sleep.gif"]


class BenCommands(commands.Cog, name="Commands"):
    """Commands for Talking Ben"""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    blacklist = app_commands.Group(name="blacklist", description="Commands for managing blacklisted channels")

    @app_commands.command(name="dmcall", description="Start a call with Ben in DMs")
    async def dmcall(self, inter: discord.Interaction) -> discord.Message:

        if self.bot.calling.get(inter.user.id):
            return await inter.response.send_message("\U0000260E There is already a call in this DM", ephemeral=True)

        await inter.response.send_message(f"\U0000260E Started a call in your DMs, {inter.user.mention}", ephemeral=True)
        self.bot.calling[inter.user.id] = True
        await inter.user.send(f"\U0000260E *Ben?*\n{self.bot.FILE_URL}/pickup.gif")
        while True:
            try:
                msg = await self.bot.wait_for(
                    "message",
                    check=lambda m: m.author != inter.client.user,
                    timeout=20,
                )
            except asyncio.TimeoutError:
                if not self.bot.calling.get(inter.user.id):
                    return

                self.bot.calling.pop(inter.user.id)
                return await inter.user.send(f"{self.bot.FILE_URL}/hangup.gif")
            resp, gif = choice(tuple(BenPhoneResponses)).value

            if self.bot.calling.get(inter.user.id):
                if randint(1, 15) == 15:
                    self.bot.calling.pop(inter.user.id, None)
                    return await inter.user.send(f"{self.bot.FILE_URL}/hangup.gif")
                await msg.reply(f"{resp}\n{self.bot.FILE_URL}/{gif}")
            else:
                break

    @app_commands.command(name="call", description="Start a phone call with Ben in your server")
    @channel_whitelisted()
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
                if not self.bot.calling.get(inter.channel.id):
                    return

                self.bot.calling.pop(inter.channel.id, None)
                return await inter.followup.send(f"{self.bot.FILE_URL}/hangup.gif")
            resp, gif = choice(tuple(BenPhoneResponses)).value

            if self.bot.calling.get(inter.channel.id):
                if randint(1, 15) == 15:
                    self.bot.calling.pop(inter.channel.id, None)
                    return await inter.followup.send(f"{self.bot.FILE_URL}/hangup.gif")
                with contextlib.suppress(discord.errors.HTTPException):
                    await msg.reply(f"{resp}\n{self.bot.FILE_URL}/{gif}")
            else:
                break

    @app_commands.command(name="end", description="End the current call")
    @channel_whitelisted()
    async def end(self, inter: discord.Interaction) -> discord.Message:
        return (
            await inter.response.send_message(f"{self.bot.FILE_URL}/hangup.gif")
            if self.bot.calling.pop(inter.channel.id if inter.guild else inter.user.id, None)
            else await inter.response.send_message("\U0000260E There is no calls currently ongoing in this channel.")
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

    @app_commands.command(name="newspaper", description="Distract Ben from his newspaper")
    async def newspaper(self, inter: discord.Interaction) -> discord.Message:
        resp, gif = choice(tuple(BenNewspaperResponses)).value
        return await inter.response.send_message(f"{resp}\n{self.bot.FILE_URL}/{gif}")

    @blacklist.command(name="add", description="Add a channel to the blacklist")
    @app_commands.describe(channel="The channel to add to the blacklist")
    @app_commands.checks.has_permissions(manage_channels=True)
    async def add(self, inter: discord.Interaction, channel: discord.TextChannel) -> discord.Message:
        async with self.bot.db.execute("SELECT channel_id FROM blacklist WHERE guild_id = ?", (inter.guild.id,)) as cursor:
            if channel.id in (list(chain(*await cursor.fetchall())) or []):
                return await inter.response.send_message("This channel is already blacklisted", ephemeral=True)
        await self.bot.db.execute("INSERT INTO blacklist (guild_id,channel_id) VALUES (?,?)", (inter.guild.id, channel.id))
        await self.bot.db.commit()
        self.bot.blacklist[inter.guild.id].append(channel.id)
        return await inter.response.send_message(f"Blacklisted channel {channel.mention}", ephemeral=True)

    @blacklist.command(name="remove", description="Remove a channel from the blacklist")
    @app_commands.describe(channel="The channel to remove from the blacklist")
    @app_commands.checks.has_permissions(manage_channels=True)
    async def remove(self, inter: discord.Interaction, channel: discord.TextChannel) -> discord.Message:
        async with self.bot.db.execute("SELECT channel_id FROM blacklist WHERE guild_id = ?", (inter.guild.id,)) as cursor:
            if channel.id not in (list(chain(*await cursor.fetchall())) or []):
                return await inter.response.send_message("This channel is not blacklisted", ephemeral=True)
        await self.bot.db.execute("DELETE FROM blacklist WHERE guild_id = ? AND channel_id = ?", (inter.guild.id, channel.id))
        await self.bot.db.commit()
        self.bot.blacklist[inter.guild.id].remove(channel.id)
        return await inter.response.send_message(f"Removed channel {channel.mention} from blacklist", ephemeral=True)

    @blacklist.command(name="list", description="Get a list of blacklisted channels in the server")
    @app_commands.checks.has_permissions(manage_channels=True)
    async def _list(self, inter: discord.Interaction) -> discord.Message:
        if g := inter.guild:
            return await inter.response.send_message(
                "__List of blacklisted channels:__\n{}".format(
                    "\n".join(map(lambda i: self.bot.get_channel(i).mention, guild_blacklist))
                )
                if (guild_blacklist := self.bot.blacklist.get(g.id))
                else "There are no blacklisted channels",
                ephemeral=True,
            )
        else:
            return await inter.response.send_message("Direct messages cannot be blacklisted", ephemeral=True)
        
    @app_commands.command(name="news", description="Create a news message")
    @app_commands.describe(image="The image URL for the news")
    @app_commands.describe(text="Optional text for the news")
    async def news(self, inter: discord.Interaction, image: str, *, text: str = None) -> discord.Message:
        await inter.response.defer()
        try:
            async with self.bot.session.get(image) as r:
                img_bytes = BytesIO(await r.read())
        except aiohttp.ClientError as e:
            return await inter.followup.send(f"\U0001f4f0 Unable to fetch image, the bot encountered an error\n`{type(e).__name__}: {e}`", ephemeral=True)

        fn = partial(generate_news, img_bytes, text)
        try:
            news = await self.bot.loop.run_in_executor(None, fn)
        except UnidentifiedImageError:
            return await inter.followup.send("\U0001f4f0 Invalid image data, unable to create news", ephemeral=True)
        return await inter.followup.send(file=discord.File(news, filename="news.png"))
        

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(BenCommands(bot))
