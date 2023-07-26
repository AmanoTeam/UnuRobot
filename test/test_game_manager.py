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

import unittest

from telegram import Chat, User

from errors import (
    AlreadyJoinedError,
    LobbyClosedError,
    NoGameInChatError,
    NotEnoughPlayersError,
)
from game_manager import GameManager


class Test(unittest.TestCase):
    game = None

    def setUp(self):
        self.gm = GameManager()

        self.chat0 = Chat(0, "group")
        self.chat1 = Chat(1, "group")
        self.chat2 = Chat(2, "group")

        self.user0 = User(0, "user0", False)
        self.user1 = User(1, "user1", False)
        self.user2 = User(2, "user2", False)

    def test_new_game(self):
        g0 = self.gm.new_game(self.chat0)
        g1 = self.gm.new_game(self.chat1)

        self.assertListEqual(self.gm.chatid_games[0], [g0])
        self.assertListEqual(self.gm.chatid_games[1], [g1])

    def test_join_game(self):
        self.assertRaises(
            NoGameInChatError,
            self.gm.join_game,
            *(self.user0, self.chat0),
        )

        g0 = self.gm.new_game(self.chat0)

        self.gm.join_game(self.user0, self.chat0)
        assert len(g0.players) == 1

        self.gm.join_game(self.user1, self.chat0)
        assert len(g0.players) == 2

        g0.open = False
        self.assertRaises(
            LobbyClosedError,
            self.gm.join_game,
            *(self.user2, self.chat0),
        )

        g0.open = True
        self.assertRaises(
            AlreadyJoinedError,
            self.gm.join_game,
            *(self.user1, self.chat0),
        )

    def test_leave_game(self):
        self.start_and_join()
        self.assertRaises(
            NotEnoughPlayersError,
            self.gm.leave_game,
            *(self.user1, self.chat0),
        )

        self.gm.join_game(self.user2, self.chat0)
        self.gm.leave_game(self.user0, self.chat0)

        self.assertRaises(
            NoGameInChatError,
            self.gm.leave_game,
            *(self.user0, self.chat0),
        )

    def test_end_game(self):
        self.start_and_join()
        assert len(self.gm.userid_players[0]) == 1

        self.gm.new_game(self.chat0)
        self.gm.join_game(self.user2, self.chat0)

        self.gm.end_game(self.chat0, self.user0)
        assert len(self.gm.chatid_games[0]) == 1

        self.gm.end_game(self.chat0, self.user2)
        assert 0 not in self.gm.chatid_games
        assert 0 not in self.gm.userid_players
        assert 1 not in self.gm.userid_players
        assert 2 not in self.gm.userid_players

    def start_and_join(self):
        self.gm.new_game(self.chat0)
        self.gm.join_game(self.user0, self.chat0)
        self.gm.join_game(self.user1, self.chat0)
