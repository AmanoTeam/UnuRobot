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

from telegram.constants import ParseMode
from telegram.ext import CommandHandler, ContextTypes

from internationalization import _, user_locale
from shared_vars import application
from user_setting import UserSetting
from utils import send_async


@user_locale
async def help_handler(update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for the /help command"""
    help_text = _(
        "Follow these steps:\n\n"
        "1. Add this bot to a group\n"
        "2. In the group, start a new game with /new or join an already"
        " running game with /join\n"
        "3. After at least two players have joined, start the game with"
        " /start\n"
        "4. Type <code>@UnuRobot</code> into your chat box and hit "
        "<b>space</b>, or click the <code>via @UnuRobot</code> text "
        "next to messages. You will see your cards (some greyed out), "
        "any extra options like drawing, and a <b>?</b> to see the "
        "current game state. The <b>greyed out cards</b> are those you "
        "<b>can not play</b> at the moment. Tap an option to execute "
        "the selected action.\n"
        "Players can join the game at any time. To leave a game, "
        "use /leave. If a player takes more than 90 seconds to play, "
        "you can use /skip to skip that player. Use /notify_me to "
        "receive a private message when a new game is started.\n\n"
        "<b>Language</b> and other settings: /settings\n"
        "Other commands (only game creator):\n"
        "/close - Close lobby\n"
        "/open - Open lobby\n"
        "/kill - Terminate the game\n"
        "/kick - Select a player to kick "
        "by replying to him or her\n"
        "/enable_translations - Translate relevant texts into all "
        "languages spoken in a game\n"
        "/disable_translations - Use English for those texts\n\n"
        "<b>Experimental:</b> Play in multiple groups at the same time. "
        "Press the <code>Current game: ...</code> button and select the "
        "group you want to play a card in.\n"
        "If you enjoy this bot, "
        '<a href="https://t.me/storebot?start=UnuRobot">'
        "rate me</a>, join the "
        '<a href="https://t.me/UnuRobotUpdates">update channel</a>'
        " and buy an UNO card game."
    )

    await send_async(
        context,
        update.message.chat_id,
        text=help_text,
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
    )


@user_locale
async def modes(update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for the /help command"""
    modes_explanation = _(
        "This UNO bot has five game modes: Classic, Sanic, Wild, Text and 7-0.\n\n"
        " 🎻 The Classic mode uses the conventional UNO deck and there is no auto skip.\n"
        " 🚀 The Sanic mode uses the conventional UNO deck and the bot automatically skips a player if he/she takes too long to play its turn\n"
        " 🐉 The Wild mode uses a deck with more special cards, less number variety and no auto skip.\n"
        " ✍️ The Text mode uses the conventional UNO deck but instead of stickers it uses the text.\n"
        " 🔫 The 7-0 mode uses the conventional UNO deck but when a player plays a 7, he/she can choose a player to swap cards with."
        " When a player plays a 0, all cards will be swapped between the current players.\n\n"
        "To change the game mode, the GAME CREATOR has to type the bot nickname and a space, "
        "just like when playing a card, and all gamemode options should appear."
    )
    await send_async(
        context,
        update.message.chat_id,
        text=modes_explanation,
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
    )


@user_locale
async def source(update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for the /help command"""
    source_text = _(
        "This bot is Free Software and licensed under the AGPL. "
        "The code is available here: \n"
        "https://github.com/AmanoTeam/UnuRobot"
    )
    attributions = _(
        "Attributions:\n"
        "Draw icon by "
        '<a href="http://www.faithtoken.com/">Faithtoken</a>\n'
        "Pass icon by "
        '<a href="http://delapouite.com/">Delapouite</a>\n'
        "Originals available on http://game-icons.net\n"
        "Icons edited by ɳick"
    )

    await send_async(
        context,
        update.message.chat_id,
        text=source_text + "\n" + attributions,
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
    )


@user_locale
async def news(update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for the /news command"""
    await send_async(
        context,
        update.message.chat_id,
        text=_("All news here: https://t.me/UnuRobotUpdates"),
        disable_web_page_preview=True,
    )


@user_locale
async def stats(update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    us = UserSetting.get(id=user.id)
    if not us or not us.stats:
        await send_async(
            context,
            update.message.chat_id,
            text=_(
                "You did not enable statistics. Use /settings in "
                "a private chat with the bot to enable them."
            ),
        )
    else:
        stats_text = list()

        n = us.games_played
        stats_text.append(
            _("{number} game played", "{number} games played", n).format(number=n)
        )

        n = us.first_places
        m = round((us.first_places / us.games_played) * 100) if us.games_played else 0
        stats_text.append(
            _(
                "{number} first place ({percent}%)",
                "{number} first places ({percent}%)",
                n,
            ).format(number=n, percent=m)
        )

        n = us.cards_played
        stats_text.append(
            _("{number} card played", "{number} cards played", n).format(number=n)
        )

        await send_async(context, update.message.chat_id, text="\n".join(stats_text))


def register():
    application.add_handler(CommandHandler("help", help_handler))
    application.add_handler(CommandHandler("source", source))
    application.add_handler(CommandHandler("news", news))
    application.add_handler(CommandHandler("stats", stats))
    application.add_handler(CommandHandler("modes", modes))
