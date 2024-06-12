import os
import pickle

from hydrogram import idle
from tortoise import run_async

from config import bot, games, player_game
from unu.db import connect_database
from unu.version import ascii_art


async def main():
    os.system("clear")
    print(ascii_art)
    await connect_database()

    if os.path.exists("cache.pkl"):
        with open("cache.pkl", 'rb') as f:
            games_cache, player_game_cache = pickle.load(f)
            games.update(games_cache)
            player_game.update(player_game_cache)

    await bot.start()
    await idle()

    # Salvar dados no cache antes de parar o bot
    with open("cache.pkl", 'wb') as f:
        pickle.dump((games, player_game), f)

    await bot.stop()


run_async(main())
