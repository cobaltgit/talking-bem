from typing import Union
from discord import app_commands
from discord import Interaction
from discord.app_commands import AppCommandError, Command, ContextMenu

async def on_app_command_error(
    interaction: Interaction,
    command: Union[Command, ContextMenu],
    error: AppCommandError
):
    error = getattr(error, "original", error)
    
    match error.__class__:
        case app_commands.CommandNotFound:
            return
        case app_commands.MissingPermissions:
            msg = f"__This command requires the following permissions__\n**{', '.join(error.missing_permissions)}**"
        case app_commands.CheckFailure:
            msg = "Required checks to run this command have failed. Perhaps you don't have permission to run it?"
            
    return await interaction.response.send_message(msg, ephemeral=True)