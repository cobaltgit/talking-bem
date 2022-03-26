import discord
from discord.ext import commands, tasks


class BackgroundTasks(commands.Cog):
    """Background tasks"""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        self.update_presence.start()

    @tasks.loop(seconds=10)
    async def update_presence(self) -> None:
        await self.bot.change_presence(
            activity=discord.Activity(name=f"over {len(self.bot.guilds)} guilds", type=discord.ActivityType.watching)
        )


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(BackgroundTasks(bot))
