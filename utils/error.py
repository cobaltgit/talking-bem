import traceback
from io import StringIO
from typing import Union

import discord
from discord import Interaction, app_commands
from discord.app_commands import AppCommandError, Command, ContextMenu


async def on_app_command_error(interaction: Interaction, command: Union[Command, ContextMenu], error: AppCommandError):
    error = getattr(error, "original", error)

    match error.__class__:
        case app_commands.CommandNotFound:
            return
        case app_commands.MissingPermissions:
            msg = "__This command requires the following permissions:__\n**{}**".format(
                "\n".join(i.replace("_", " ").replace("guild", "server").title() for i in error.missing_permissions)
            )
        case app_commands.CheckFailure:
            msg = str(error)
        case _:
            f = discord.File(StringIO(traceback.format_exc()), filename="exception.py")
            await interaction.response.defer()
            return await interaction.followup.send(file=f, ephemeral=True)

    return await interaction.response.send_message(msg, ephemeral=True)
