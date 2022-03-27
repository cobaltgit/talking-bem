from io import StringIO

import discord
from discord.ext import app_commands, commands


class ErrorHandler(commands.Cog):
    """Error handler cog"""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error: commands.CommandError) -> discord.Message | None:
        error = getattr(error, "original", error)
        if isinstance(error, (app_commands.CommandNotFound, commands.CommandNotFound)):
            return
        elif isinstance(error, (commands.CheckFailure, app_commands.CheckFailure)):
            return await ctx.send("Check failure: you lack necessary permissions to run this command!")
        else:
            raise error


def setup(bot: commands.Bot) -> None:
    bot.add_cog(ErrorHandler(bot))
