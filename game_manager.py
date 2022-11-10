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

import contextlib
import logging

from telegram import Chat

from errors import (
    AlreadyJoinedError,
    LobbyClosedError,
    NoGameInChatError,
    NotEnoughPlayersError,
)
from game import Game
from player import Player


class GameManager:
    """Manages all running games by using a confusing amount of dicts"""

    def __init__(self):
        self.chatid_games = {}
        self.userid_players = {}
        self.userid_current = {}
        self.remind_dict = {}

        self.logger = logging.getLogger(__name__)

    def new_game(self, chat: Chat, thread_id: int = None):
        """
        Create a new game in this chat
        """
        chat_id = chat.id

        self.logger.debug("Creating new game in chat %s", str(chat_id))
        game = Game(chat, thread_id)

        if chat_id not in self.chatid_games:
            self.chatid_games[chat_id] = []

        # remove old games
        for g in list(self.chatid_games[chat_id]):
            if not g.players:
                self.chatid_games[chat_id].remove(g)

        self.chatid_games[chat_id].append(game)
        return game

    def join_game(self, user, chat):
        """Create a player from the Telegram user and add it to the game"""
        self.logger.info("Joining game with id %s", chat.id)

        try:
            game = self.chatid_games[chat.id][-1]
        except (KeyError, IndexError) as e:
            raise NoGameInChatError() from e

        if not game.open:
            raise LobbyClosedError()

        if user.id not in self.userid_players:
            self.userid_players[user.id] = []

        players = self.userid_players[user.id]

        # Don not re-add a player and remove the player from previous games in
        # this chat, if he is in one of them
        for player in players:
            if player in game.players:
                raise AlreadyJoinedError()

        try:
            self.leave_game(user, chat)
        except NoGameInChatError:
            pass
        except NotEnoughPlayersError:
            self.end_game(chat, user)

            if user.id not in self.userid_players:
                self.userid_players[user.id] = []

            players = self.userid_players[user.id]

        player = Player(game, user)
        if game.started:
            player.draw_first_hand()

        players.append(player)
        self.userid_current[user.id] = player

    def leave_game(self, user, chat):
        """Remove a player from its current game"""

        player = self.player_for_user_in_chat(user, chat)
        players = self.userid_players.get(user.id, [])

        if not player:
            games = self.chatid_games[chat.id]
            for g in games:
                for p in g.players:
                    if p.user.id == user.id:
                        if p is g.current_player:
                            g.turn()

                        p.leave()
                        return

            raise NoGameInChatError

        game = player.game

        if len(game.players) < 3:
            raise NotEnoughPlayersError()

        if player is game.current_player:
            game.turn()

        player.leave()
        players.remove(player)

        # If this is the selected game, switch to another
        if self.userid_current.get(user.id) is player:
            if players:
                self.userid_current[user.id] = players[0]
            else:
                del self.userid_current[user.id]
                del self.userid_players[user.id]

    def end_game(self, chat, user):
        """
        End a game
        """

        self.logger.info("Game in chat %s ended", chat.id)

        # Find the correct game instance to end
        player = self.player_for_user_in_chat(user, chat)

        if not player:
            raise NoGameInChatError

        game = player.game

        # Clear game
        for player_in_game in game.players:
            this_users_players = self.userid_players.get(player_in_game.user.id, [])

            with contextlib.suppress(ValueError):
                this_users_players.remove(player_in_game)
            if this_users_players:
                with contextlib.suppress(KeyError):
                    self.userid_current[player_in_game.user.id] = this_users_players[0]
            else:
                with contextlib.suppress(KeyError):
                    del self.userid_players[player_in_game.user.id]
                with contextlib.suppress(KeyError):
                    del self.userid_current[player_in_game.user.id]
        self.chatid_games[chat.id].remove(game)
        if not self.chatid_games[chat.id]:
            del self.chatid_games[chat.id]

    def player_for_user_in_chat(self, user, chat):
        players = self.userid_players.get(user.id, [])
        return next(
            (player for player in players if player.game.chat.id == chat.id), None
        )
