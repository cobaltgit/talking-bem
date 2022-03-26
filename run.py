import asyncio

from bot import Ben


async def boot() -> None:
    async with Ben() as bot:
        return await bot.start(bot.config.get("token"))


asyncio.run(boot())
