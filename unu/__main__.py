import os

from hydrogram import idle
from tortoise import run_async

from config import bot
from unu.db import connect_database
from unu.utils import load_all, save_all
from unu.version import ascii_art


async def main():
    os.system("clear")
    print(ascii_art)
    await connect_database()
    await bot.start()
    await load_all()

    await idle()

    await save_all()
    await bot.stop()


run_async(main())
