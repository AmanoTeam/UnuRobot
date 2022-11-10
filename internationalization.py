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


import gettext
from functools import wraps

from pony.orm import db_session
from telegram import Update
from telegram.ext import ContextTypes

from locales import available_locales
from shared_vars import gm
from user_setting import UserSetting

GETTEXT_DOMAIN = "unobot"
GETTEXT_DIR = "locales"


class _Underscore(object):
    """Class to emulate flufl.i18n behaviour, but with plural support"""

    def __init__(self):
        self.translators = {
            locale: gettext.GNUTranslations(
                open(
                    gettext.find(GETTEXT_DOMAIN, GETTEXT_DIR, languages=[locale]), "rb"
                )
            )
            for locale in available_locales.keys()
            if locale != "en_US"  # No translation file for en_US
        }
        self.locale_stack = list()

    def push(self, locale):
        self.locale_stack.append(locale)

    def pop(self):
        if self.locale_stack:
            return self.locale_stack.pop()
        else:
            return None

    @property
    def code(self):
        if self.locale_stack:
            return self.locale_stack[-1]
        else:
            return None

    def __call__(self, singular, plural=None, n=1, locale=None):
        if not locale:
            locale = self.locale_stack[-1]

        if locale not in self.translators.keys():
            if n == 1:
                return singular
            else:
                return plural

        translator = self.translators[locale]

        if plural is None:
            return translator.gettext(singular)
        else:
            return translator.ngettext(singular, plural, n)


_ = _Underscore()


def __(singular, plural=None, n=1, multi=False):
    """Translates text into all locales on the stack"""
    translations = list()

    if not multi and len(set(_.locale_stack)) >= 1:
        translations.append(_(singular, plural, n, "en_US"))

    else:
        for locale in _.locale_stack:
            translation = _(singular, plural, n, locale)

            if translation not in translations:
                translations.append(translation)

    return "\n".join(translations)


def user_locale(func):
    @wraps(func)
    async def wrapped(
        update: Update, context: ContextTypes.DEFAULT_TYPE, *pargs, **kwargs
    ):
        user = _user_chat_from_update(update)[0]

        with db_session:
            us = UserSetting.get(id=user.id)

            if us and us.lang != "en":
                _.push(us.lang)
            else:
                _.push("en_US")

            result = await func(update, context, *pargs, **kwargs)
        _.pop()
        return result

    return wrapped


def game_locales(func):
    @wraps(func)
    async def wrapped(
        update: Update, context: ContextTypes.DEFAULT_TYPE, *pargs, **kwargs
    ):
        user, chat = _user_chat_from_update(update)
        player = gm.player_for_user_in_chat(user, chat)
        locales = list()

        if player:
            for player in player.game.players:
                with db_session:
                    us = UserSetting.get(id=player.user.id)

                if us and us.lang != "en":
                    loc = us.lang
                else:
                    loc = "en_US"

                if loc in locales:
                    continue

                _.push(loc)
                locales.append(loc)

        result = await func(update, context, *pargs, **kwargs)

        while _.code:
            _.pop()

        return result

    return wrapped


def _user_chat_from_update(update):
    try:
        user = update.message.from_user
        chat = update.message.chat
    except (NameError, AttributeError):
        try:
            user = update.inline_query.from_user
            chat = gm.userid_current[user.id].game.chat
        except KeyError:
            chat = None
        except (NameError, AttributeError):
            try:
                user = update.chosen_inline_result.from_user
                chat = gm.userid_current[user.id].game.chat
            except (NameError, AttributeError, KeyError):
                chat = None

    return user, chat
