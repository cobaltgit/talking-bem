from itertools import cycle
import discord
from discord.ext import commands, tasks


class BackgroundTasks(commands.Cog):
    """Background tasks"""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.tasks = [self.update_presence]
        self._presences = [
            "over {guild_count} servers",
            "support server - https://discord.gg/cq4VawvptQ",
            "top.gg - https://top.gg/bot/955078353700937778",
            "source code - https://github.com/cobaltgit/talking-ben"
        ]
        self.presences = cycle(self._presences)

    async def cog_load(self) -> None:
        for t in self.tasks:
            t.start()

    @tasks.loop(seconds=30)
    async def update_presence(self) -> None:
        await self.bot.wait_until_ready()
        FORMATS = {
            "guild_count": len(self.bot.guilds),
        }
        await self.bot.change_presence(
            activity=discord.Activity(name=next(self.presences).format(**FORMATS), type=discord.ActivityType.watching)
        )


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(BackgroundTasks(bot))
