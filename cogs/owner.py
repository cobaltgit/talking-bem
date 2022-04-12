import discord
from discord.ext import commands


class Owner(commands.Cog):
    """Owner-only commands, usually used for debugging"""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.command(name="synctree")
    @commands.is_owner()
    async def synctree(self, ctx: commands.Context, *guild_ids) -> discord.Message:
        """Sync the application command tree"""
        if not guild_ids:
            await self.bot.tree.sync()
        else:
            for i in map(int, guild_ids):
                await self.bot.tree.sync(guild=discord.Object(id=i))
        await ctx.message.delete()
        return await ctx.send("Command tree synced!", delete_after=10)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Owner(bot))
