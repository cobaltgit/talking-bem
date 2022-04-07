import sys

if sys.version_info < (3, 10):
    raise RuntimeError("Python 3.10 or higher is required to use this bot")

import asyncio
from collections import defaultdict
from typing import DefaultDict

import aiosqlite

from bot import Ben


async def cache_blacklist(cursor: aiosqlite.Cursor) -> DefaultDict[int, list[int]]:
    _blacklist = defaultdict(list)
    async for g, c in cursor:
        _blacklist[g].append(c)
    return _blacklist


async def _boot() -> None:
    async with Ben() as bot:
        async with aiosqlite.connect("db/main.db") as bot.db:
            with open("db/schema.sql", "r", encoding="utf-8") as schema:
                await bot.db.executescript(schema.read())
            async with bot.db.execute("SELECT * FROM blacklist") as cursor:
                bot.blacklist = await cache_blacklist(cursor)
            await bot.start(bot.config.get("token"))


asyncio.run(_boot())
