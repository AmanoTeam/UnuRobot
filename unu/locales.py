import os
from functools import partial, wraps
from glob import glob
from typing import TYPE_CHECKING

import yaml
from hydrogram.enums import ChatType
from hydrogram.types import Message

from config import player_game
from unu.db import Chat, User

if TYPE_CHECKING:
    from unu.game import Game

langs = ["en-US", "pt-BR"]

default_language = "en-US"


def cache_localizations(files: list[str]) -> dict[str, dict[str, dict[str, str]]]:
    ldict = {lang: {} for lang in langs}
    for file in files:
        _, pname = file.split(os.path.sep)
        lang = pname.split(".")[0]
        with open(file, encoding="locale") as f:
            ldict[lang] = yaml.safe_load(f)
    return ldict


jsons = []

for locale in langs:
    jsons += glob(os.path.join("locales", f"{locale}.yml"))

langdict = cache_localizations(jsons)


def use_lang():
    def decorator(func):
        @wraps(func)
        async def wrapper(client, message):
            ulang = (await User.get_or_create(id=message.from_user.id))[0].lang
            if not isinstance(message, Message):
                if message.from_user.id not in player_game:
                    clang = ulang
                else:
                    game: Game = player_game[message.from_user.id]
                    chatid = game.chat.id
                    clang = (await Chat.get_or_create(id=chatid))[0].lang
            else:
                clang = (await Chat.get_or_create(id=message.chat.id))[0].lang
            ulfunc = partial(get_locale_string, ulang)
            clfunc = partial(get_locale_string, clang)
            return await func(client, message, ulfunc, clfunc)

        return wrapper

    return decorator


def use_chat_lang():
    def decorator(func):
        @wraps(func)
        async def wrapper(client, message):
            mmessage = message.message if not isinstance(message, Message) else message
            if mmessage.chat.type == ChatType.PRIVATE:
                clang = (await User.get_or_create(id=mmessage.chat.id))[0].lang
            else:
                clang = (await Chat.get_or_create(id=mmessage.chat.id))[0].lang
            clfunc = partial(get_locale_string, clang)
            return await func(client, message, clfunc)

        return wrapper

    return decorator


def use_user_lang():
    def decorator(func):
        @wraps(func)
        async def wrapper(client, message):
            ulang = (await User.get_or_create(id=message.from_user.id))[0].lang
            ulfunc = partial(get_locale_string, ulang)
            return await func(client, message, ulfunc)

        return wrapper

    return decorator


def get_locale_string(language: str, key: str) -> str:
    print(f"Getting {key} for {language}")
    res: str = langdict[language].get(key) or key
    return res
