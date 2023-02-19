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

from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import CommandHandler, ContextTypes, MessageHandler, filters

from internationalization import _, user_locale
from locales import available_locales
from shared_vars import application
from user_setting import UserSetting
from utils import send_async


@user_locale
async def show_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.message.chat

    if update.message.chat.type != "private":
        await send_async(
            chat,
            text=_("Please edit your settings in a private chat with " "the bot."),
            message_thread_id=update.message.message_thread_id,
        )
        return

    us = UserSetting.get(id=update.message.from_user.id)

    if not us:
        us = UserSetting(id=update.message.from_user.id)

    stats = (
        "❌" + " " + _("Delete all statistics")
        if us.stats
        else "📊" + " " + _("Enable statistics")
    )

    kb = [[stats], ["🌍" + " " + _("Language")]]
    await send_async(
        chat,
        text="🔧" + " " + _("Settings"),
        reply_markup=ReplyKeyboardMarkup(keyboard=kb, one_time_keyboard=True),
    )


@user_locale
async def kb_select(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.message.chat
    user = update.message.from_user
    option = context.matches[0].group(1)

    if option == "📊":
        us = UserSetting.get(id=user.id)
        us.stats = True
        await send_async(chat, text=_("Enabled statistics!"))

    elif option == "🌍":
        kb = [
            [f"{locale} - {descr}"]
            for locale, descr in sorted(available_locales.items())
        ]

        await send_async(
            chat,
            text=_("Select locale"),
            reply_markup=ReplyKeyboardMarkup(keyboard=kb, one_time_keyboard=True),
        )

    elif option == "❌":
        us = UserSetting.get(id=user.id)
        us.stats = False
        us.first_places = 0
        us.games_played = 0
        us.cards_played = 0
        await send_async(chat, text=_("Deleted and disabled statistics!"))


@user_locale
async def locale_select(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.message.chat
    user = update.message.from_user
    option = context.matches[0].group(1)

    if option in available_locales:
        us = UserSetting.get(id=user.id)
        us.lang = option
        _.push(option)
        await send_async(chat, text=_("Set locale!"))
        _.pop()


def register():
    application.add_handler(CommandHandler("settings", show_settings))
    application.add_handler(MessageHandler(filters.Regex(r"^([📊🌍❌]) .+$"), kb_select))
    application.add_handler(
        MessageHandler(filters.Regex(r"^(\w\w(_\w\w)?) - .*"), locale_select)
    )
