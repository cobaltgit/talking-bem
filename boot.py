import sys

if sys.version_info < (3, 10):
    raise RuntimeError("Python 3.10 or higher is required to use this bot")

import asyncio

from bot import Ben


async def _boot() -> None:
    async with Ben() as bot:
        await bot.start(bot.config.get("token"))


asyncio.run(_boot())
