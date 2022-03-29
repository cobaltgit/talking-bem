import discord
from discord.ext import commands, tasks
from itertools import cycle


class BackgroundTasks(commands.Cog):
    """Background tasks"""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.presences = cycle([
            f"Taking calls in {len(bot.guilds)} guilds", 
            "Vote me on top.gg! https://top.gg/bot/955078353700937778", 
            "Source code: https://github.com/cobaltgit/talking-ben"
        ])
        self.tasks = [self.update_presence]

    async def cog_load(self) -> None:
        for t in self.tasks:
            t.start()

    @tasks.loop(seconds=30)
    async def update_presence(self) -> None:
        await self.bot.change_presence(
            activity=discord.Activity(name=next(self.presences), type=discord.ActivityType.watching)
        )

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(BackgroundTasks(bot))