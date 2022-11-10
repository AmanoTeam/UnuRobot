#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Telegram bot to play UNO in group chats
# Copyright (c) 2016 Jannes Höke <uno@jhoeke.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import logging
from typing import Union

from telegram import Chat, Update, User
from telegram.ext import ContextTypes

from game import Game
from internationalization import _, __
from mwt import MWT
from shared_vars import gm

logger = logging.getLogger(__name__)

TIMEOUT = 2.5


def list_subtract(list1, list2):
    """Helper function to subtract two lists and return the sorted result"""
    list1 = list1.copy()

    for x in list2:
        list1.remove(x)

    return list(sorted(list1))


def display_name(user):
    """Get the current players name including their username, if possible"""
    user_name = user.first_name
    if user.username:
        user_name += f" (@{user.username})"
    return user_name


def display_color(color):
    """Convert a color code to actual color name"""
    if color == "r":
        return _("{emoji} Red").format(emoji="❤️")
    if color == "b":
        return _("{emoji} Blue").format(emoji="💙")
    if color == "g":
        return _("{emoji} Green").format(emoji="💚")
    if color == "y":
        return _("{emoji} Yellow").format(emoji="💛")


def display_color_group(color, game):
    """Convert a color code to actual color name"""
    if color == "r":
        return __("{emoji} Red", game.translate).format(emoji="❤️")
    if color == "b":
        return __("{emoji} Blue", game.translate).format(emoji="💙")
    if color == "g":
        return __("{emoji} Green", game.translate).format(emoji="💚")
    if color == "y":
        return __("{emoji} Yellow", game.translate).format(emoji="💛")


def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Simple error handler"""
    if isinstance(context, Exception):
        logger.exception(context)
    else:
        logger.exception(context.error)


async def send_async(context: Union[Game, Chat, User], *args, **kwargs):
    """Send a message asynchronously"""

    if isinstance(context, Game) and not kwargs.get("message_thread_id"):
        kwargs["message_thread_id"] = context.thread_id

    chat = context.chat if isinstance(context, Game) else context
    try:
        await chat.send_message(*args, **kwargs)
    except Exception as e:
        error(None, e)


async def answer_async(context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
    """Answer an inline query asynchronously"""
    try:
        await context.bot.answer_inline_query(*args, **kwargs)
    except Exception as e:
        error(None, e)


def game_is_running(game):
    return game in gm.chatid_games.get(game.chat.id, [])


def user_is_creator(user, game):
    return user.id in game.owner


async def user_is_admin(user, context, chat):
    return user.id in await get_admin_ids(context, chat.id)


async def user_is_creator_or_admin(user, game, context, chat):
    return user_is_creator(user, game) or await user_is_admin(user, context, chat)


@MWT(timeout=60 * 60)
async def get_admin_ids(context, chat_id):
    """Returns a list of admin IDs for a given chat. Results are cached for 1 hour."""
    return [
        admin.user.id for admin in await context.bot.get_chat_administrators(chat_id)
    ]
