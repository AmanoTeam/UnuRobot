from config import bot
from hydrogram import idle
from tortoise import run_async
from version import ascii_art
from db import connect_database
import os


async def main():
    os.system("clear")
    print(ascii_art)
    await connect_database()
    await bot.start()
    await idle()
    await bot.stop()


run_async(main())
