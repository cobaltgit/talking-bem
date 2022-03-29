import discord
from discord.ext import commands, tasks


class BackgroundTasks(commands.Cog):
    """Background tasks"""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.tasks = [self.update_presence]

    async def cog_load(self) -> None:
        for t in self.tasks:
            t.start()

    @tasks.loop(seconds=10)
    async def update_presence(self) -> None:
        await self.bot.wait_until_ready()
        await self.bot.change_presence(
            activity=discord.Activity(name=f"over {len(self.bot.guilds)} guilds", type=discord.ActivityType.watching)
        )

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(BackgroundTasks(bot))