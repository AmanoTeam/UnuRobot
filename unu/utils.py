from hydrogram import Client, filters
from hydrogram.types import Message

from config import games, player_game, sudoers
from unu.db import GameModel, GamePlayer, User
from unu.game import Game


async def filter_sudoers_logic(flt, c: Client, m: Message):
    if not m.from_user:
        return None
    usr = m.from_user
    db_usr = await User.get_or_none(id=usr.id)
    if not db_usr:
        return False
    return bool(db_usr.sudo or usr.id in sudoers)


filter_sudoers = filters.create(filter_sudoers_logic, "FilterSudoers")


__all__ = ["filter_sudoers"]


async def save_all():
    for game in games.values():
        await game.save()
    for chat_id, game in player_game.items():
        await GamePlayer.create(player_id=chat_id, game_chat_id=game.chat.id)


async def load_all():
    # Carregar dados do cache
    for game in await GameModel.all():
        try:
            sgame = await Game.load(game)
            games[int(sgame.chat.id)] = sgame
            await game.delete()
        except:
            continue

    for player in await GamePlayer.all():
        if player.game_chat_id in games:
            player_game[player.player_id] = games[player.game_chat_id]
            await player.delete()
