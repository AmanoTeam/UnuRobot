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


# Colors
import json

COLORS = ("r", "b", "g", "y")

COLOR_ICONS = {
    "r": '❤️',
    "b": '💙',
    "g": '💚',
    "y": '💛',
    "x": '⬛️'
}

VALUES = ('0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'draw',
          'reverse', 'skip')
WILD_VALUES = ('1', '2', '3', '4', '5', 'draw', 'reverse', 'skip')

with open("cards.json", "r") as fp:
        cards = json.load(fp)

STICKERS=cards["minimalist"]["STICKERS"]
STICKERS_GREY=cards["minimalist"]["STICKERS_GREY"]

class Card(object):
    """This class represents an UNO card"""

    def __init__(self, color, value, special=None):
        self.color = color
        self.value = value
        self.special = special

    def __str__(self):
        if self.special:
            return self.special
        else:
            return '%s_%s' % (self.color, self.value)

    def __repr__(self):
        if self.special:
            return '%s%s%s' % (COLOR_ICONS.get(self.color, ''),
                               COLOR_ICONS["x"],
                               ' '.join([s.capitalize()
                                         for s in self.special.split('_')]))
        else:
            return '%s%s' % (COLOR_ICONS[self.color], self.value.capitalize())

    def __eq__(self, other):
        """Needed for sorting the cards"""
        return str(self) == str(other)

    def __lt__(self, other):
        """Needed for sorting the cards"""
        return str(self) < str(other)


def from_str(string, theme):
    """Decodes a Card object from a string"""
    if string not in cards[list(cards)[theme]]["SPECIALS"]:
        color, value = string.split('_')
        return Card(color, value)
    else:
        return Card(None, None, string)
