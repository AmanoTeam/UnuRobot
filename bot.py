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
from datetime import datetime

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.constants import ParseMode
from telegram.ext import (
    CallbackQueryHandler,
    ChosenInlineResultHandler,
    CommandHandler,
    ContextTypes,
    InlineQueryHandler,
    MessageHandler,
    filters,
)

import card as c
import settings
import simple_commands
from actions import (
    do_call_bluff,
    do_draw,
    do_play_card,
    do_skip,
    remove_cards,
    start_player_countdown,
    subport,
)
from config import DEFAULT_GAMEMODE, MIN_PLAYERS, WAITING_TIME
from errors import (
    AlreadyJoinedError,
    DeckEmptyError,
    LobbyClosedError,
    NoGameInChatError,
    NotEnoughPlayersError,
)
from internationalization import _, __, game_locales, user_locale
from results import (
    add_call_bluff,
    add_card,
    add_choose_color,
    add_choose_player,
    add_draw,
    add_gameinfo,
    add_mode_classic,
    add_mode_fast,
    add_mode_sete,
    add_mode_text,
    add_mode_wild,
    add_no_game,
    add_not_started,
    add_other_cards,
    add_pass,
)
from shared_vars import application, gm
from simple_commands import help_handler
from utils import (
    answer_async,
    display_name,
    error,
    game_is_running,
    send_async,
    user_is_creator,
    user_is_creator_or_admin,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


@user_locale
async def notify_me(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for /notify_me command, pm people for next game"""
    chat = update.message.chat

    if update.message.chat.type == "private":
        await send_async(
            chat,
            text=_(
                "Send this command in a group to be notified "
                "when a new game is started there."
            ),
            message_thread_id=update.message.message_thread_id,
        )
    else:
        try:
            gm.remind_dict[chat.id].add(update.message.from_user.id)
        except KeyError:
            gm.remind_dict[chat.id] = {update.message.from_user.id}


@user_locale
async def new_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for the /new command"""

    if update.message.chat.type == "private":
        await help_handler(update, context)

    else:

        if update.message.chat_id in gm.remind_dict:
            for user in gm.remind_dict[update.message.chat_id]:
                await send_async(
                    user,
                    text=_("A new game has been started in {title}").format(
                        title=update.message.chat.title
                    ),
                )

            del gm.remind_dict[update.message.chat_id]

        game = gm.new_game(update.message.chat, update.message.message_thread_id)
        game.starter = update.message.from_user
        game.owner.append(update.message.from_user.id)
        game.mode = DEFAULT_GAMEMODE
        await send_async(
            game,
            text=_(
                "Created a new game! Join the game with /join "
                "and start the game with /start"
            ),
        )


@user_locale
async def kill_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for the /kill command"""
    chat = update.message.chat
    user = update.message.from_user
    games = gm.chatid_games.get(chat.id)

    if update.message.chat.type == "private":
        await help_handler(update, context)
        return

    if not games:
        await send_async(
            chat,
            text=_("There is no running game in this chat."),
            message_thread_id=update.message.message_thread_id,
        )
        return

    game = games[-1]

    if await user_is_creator_or_admin(user, game, context, chat):

        try:
            gm.end_game(chat, user)
            await send_async(game, text=__("Game ended!", multi=game.translate))

        except NoGameInChatError:
            await send_async(
                game,
                text=_(
                    "The game is not started yet. "
                    "Join the game with /join and start the game with /start"
                ),
                reply_to_message_id=update.message.message_id,
            )

    else:
        await send_async(
            game,
            text=_("Only the game creator ({name}) and admin can do that.").format(
                name=game.starter.first_name
            ),
            reply_to_message_id=update.message.message_id,
        )


@user_locale
async def join_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for the /join command"""
    chat = update.message.chat

    if update.message.chat.type == "private":
        await help_handler(update, context)
        return

    try:
        gm.join_game(update.message.from_user, chat)

    except LobbyClosedError:
        await send_async(
            chat,
            text=_("The lobby is closed"),
            message_thread_id=update.message.message_thread_id,
        )

    except NoGameInChatError:
        await send_async(
            chat,
            text=_("No game is running at the moment. " "Create a new game with /new"),
            message_thread_id=update.message.message_thread_id,
            reply_to_message_id=update.message.message_id,
        )

    except AlreadyJoinedError:
        await send_async(
            chat,
            text=_("You already joined the game. Start the game " "with /start"),
            message_thread_id=update.message.message_thread_id,
            reply_to_message_id=update.message.message_id,
        )

    except DeckEmptyError:
        await send_async(
            chat,
            text=_(
                "There are not enough cards left in the deck for "
                "new players to join."
            ),
            message_thread_id=update.message.message_thread_id,
            reply_to_message_id=update.message.message_id,
        )

    else:
        await send_async(
            chat,
            text=_("Joined the game"),
            message_thread_id=update.message.message_thread_id,
            reply_to_message_id=update.message.message_id,
        )


@user_locale
async def leave_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for the /leave command"""
    chat = update.message.chat
    user = update.message.from_user

    player = gm.player_for_user_in_chat(user, chat)

    if player is None:
        await send_async(
            chat,
            text=_("You are not playing in a game in " "this group."),
            message_thread_id=update.message.message_thread_id,
            reply_to_message_id=update.message.message_id,
        )
        return

    game = player.game
    user = update.message.from_user

    try:
        gm.leave_game(user, chat)

    except NoGameInChatError:
        await send_async(
            game,
            text=_("You are not playing in a game in " "this group."),
            reply_to_message_id=update.message.message_id,
        )

    except NotEnoughPlayersError:
        gm.end_game(chat, user)
        await send_async(game, text=__("Game ended!", multi=game.translate))

    else:
        if game.started:
            await send_async(
                game,
                text=__("Okay. Next Player: {name}", multi=game.translate).format(
                    name=display_name(game.current_player.user)
                ),
                reply_to_message_id=update.message.message_id,
            )
        else:
            await send_async(
                game,
                text=__(
                    "{name} left the game before it started.", multi=game.translate
                ).format(name=display_name(user)),
                reply_to_message_id=update.message.message_id,
            )


@user_locale
async def kick_player(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for the /kick command"""

    if update.message.chat.type == "private":
        await help_handler(update, context)
        return

    chat = update.message.chat
    user = update.message.from_user

    try:
        game = gm.chatid_games[chat.id][-1]

    except (KeyError, IndexError):
        await send_async(
            chat,
            text=_("No game is running at the moment. " "Create a new game with /new"),
            message_thread_id=update.message.message_thread_id,
            reply_to_message_id=update.message.message_id,
        )
        return

    if not game.started:
        await send_async(
            game,
            text=_(
                "The game is not started yet. "
                "Join the game with /join and start the game with /start"
            ),
            reply_to_message_id=update.message.message_id,
        )
        return

    if await user_is_creator_or_admin(user, game, context, chat):

        if update.message.reply_to_message:
            kicked = update.message.reply_to_message.from_user

            try:
                gm.leave_game(kicked, chat)

            except NoGameInChatError:
                await send_async(
                    game,
                    text=_(
                        "Player {name} is not found in the current game.".format(
                            name=display_name(kicked)
                        )
                    ),
                    reply_to_message_id=update.message.message_id,
                )
                return

            except NotEnoughPlayersError:
                gm.end_game(chat, user)
                await send_async(
                    game,
                    text=_(
                        "{0} was kicked by {1}".format(
                            display_name(kicked), display_name(user)
                        )
                    ),
                )
                await send_async(game, text=__("Game ended!", multi=game.translate))
                return

            await send_async(
                game,
                text=_(
                    "{0} was kicked by {1}".format(
                        display_name(kicked), display_name(user)
                    )
                ),
            )

        else:
            await send_async(
                game,
                text=_(
                    "Please reply to the person you want to kick and type /kick again."
                ),
                reply_to_message_id=update.message.message_id,
            )
            return

        await send_async(
            game,
            text=__("Okay. Next Player: {name}", multi=game.translate).format(
                name=display_name(game.current_player.user)
            ),
            reply_to_message_id=update.message.message_id,
        )

    else:
        await send_async(
            game,
            text=_("Only the game creator ({name}) and admin can do that.").format(
                name=game.starter.first_name
            ),
            reply_to_message_id=update.message.message_id,
        )


async def select_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for callback queries to select the current game"""

    chat_id = int(update.callback_query.data)
    user_id = update.callback_query.from_user.id
    players = gm.userid_players[user_id]
    for player in players:
        if player.game.chat.id == chat_id:
            gm.userid_current[user_id] = player
            break
    else:
        await send_async(
            update.callback_query.message.chat,
            text=_("Game not found."),
            message_thread_id=update.message.message_thread_id,
        )
        return

    async def selected(bot):
        back = [
            [InlineKeyboardButton(text=_("Back to last group"), switch_inline_query="")]
        ]
        await context.bot.answerCallbackQuery(
            update.callback_query.id,
            text=_("Please switch to the group you selected!"),
            show_alert=False,
        )

        await context.bot.editMessageText(
            chat_id=update.callback_query.message.chat_id,
            message_id=update.callback_query.message.message_id,
            text=_(
                "Selected group: {group}\n"
                "<b>Make sure that you switch to the correct "
                "group!</b>"
            ).format(group=gm.userid_current[user_id].game.chat.title),
            reply_markup=InlineKeyboardMarkup(back),
            parse_mode=ParseMode.HTML,
        )

    await selected(context.bot)


@game_locales
async def status_update(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Remove player from game if user leaves the group"""
    chat = update.message.chat

    user = update.message.left_chat_member

    try:
        gm.leave_game(user, chat)
        game = gm.player_for_user_in_chat(user, chat).game

    except NoGameInChatError:
        pass
    except NotEnoughPlayersError:
        gm.end_game(chat, user)
        await send_async(
            chat,
            text=__("Game ended!", multi=game.translate),
            message_thread_id=update.message.message_thread_id,
        )
    else:
        await send_async(
            game,
            text=__("Removing {name} from the game", multi=game.translate).format(
                name=display_name(user)
            ),
        )


@game_locales
@user_locale
async def start_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for the /start command"""

    args = context.args

    if update.message.chat.type != "private":
        chat = update.message.chat

        try:
            game = gm.chatid_games[chat.id][-1]
        except (KeyError, IndexError):
            await send_async(
                chat,
                text=_(
                    "There is no game running in this chat. Create "
                    "a new one with /new"
                ),
            )
            return

        if game.started:
            await send_async(game, text=_("The game has already started"))

        elif len(game.players) < MIN_PLAYERS:
            await send_async(
                game,
                text=__(
                    "At least {minplayers} players must /join the game "
                    "before you can start it"
                ).format(minplayers=MIN_PLAYERS),
            )

        else:
            # Starting a game
            game.start()

            for player in game.players:
                player.draw_first_hand()
            choice = [
                [
                    InlineKeyboardButton(
                        text=_("Make your choice!"), switch_inline_query_current_chat=""
                    )
                ]
            ]
            first_message = __(
                "First player: {name}\n"
                "Use /close to stop people from joining the game.\n"
                "Enable multi-translations with /enable_translations",
                multi=game.translate,
            ).format(name=display_name(game.current_player.user))

            async def send_first():
                """Send the first card and player"""

                await context.bot.send_sticker(
                    chat.id,
                    sticker=c.STICKERS[str(game.last_card)],
                    message_thread_id=game.thread_id,
                )

                await send_async(
                    game,
                    text=first_message,
                    reply_markup=InlineKeyboardMarkup(choice),
                )

            await send_first()
            start_player_countdown(context, game)

    elif len(args) and args[0] == "select":
        players = gm.userid_players[update.message.from_user.id]

        groups = []
        for player in players:
            title = player.game.chat.title

            if player is gm.userid_current[update.message.from_user.id]:
                title = f"- {player.game.chat.title} -"

            groups.append(
                [
                    InlineKeyboardButton(
                        text=title, callback_data=str(player.game.chat.id)
                    )
                ]
            )

        await send_async(
            game,
            text=_("Please select the group you want to play in."),
            reply_markup=InlineKeyboardMarkup(groups),
        )

    else:
        await help_handler(update, context)


@user_locale
async def close_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for the /close command"""
    chat = update.message.chat
    user = update.message.from_user
    games = gm.chatid_games.get(chat.id)

    if not games:
        await send_async(
            chat,
            text=_("There is no running game in this chat."),
            message_thread_id=update.message.message_thread_id,
        )
        return

    game = games[-1]

    if user.id in game.owner:
        game.open = False
        await send_async(
            game,
            text=_("Closed the lobby. " "No more players can join this game."),
        )
    else:
        await send_async(
            game,
            text=_("Only the game creator ({name}) and admin can do that.").format(
                name=game.starter.first_name
            ),
            reply_to_message_id=update.message.message_id,
        )

    return


@user_locale
async def open_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for the /open command"""
    chat = update.message.chat
    user = update.message.from_user
    games = gm.chatid_games.get(chat.id)

    if not games:
        await send_async(
            chat,
            text=_("There is no running game in this chat."),
            message_thread_id=update.message.message_thread_id,
        )
        return

    game = games[-1]

    if user.id in game.owner:
        game.open = True
        await send_async(
            game,
            text=_("Opened the lobby. " "New players may /join the game."),
        )
    else:
        await send_async(
            game,
            text=_("Only the game creator ({name}) and admin can do that.").format(
                name=game.starter.first_name
            ),
            reply_to_message_id=update.message.message_id,
        )

    return


@user_locale
async def enable_translations(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for the /enable_translations command"""
    chat = update.message.chat
    user = update.message.from_user
    games = gm.chatid_games.get(chat.id)

    if not games:
        await send_async(
            chat,
            text=_("There is no running game in this chat."),
            message_thread_id=update.message.message_thread_id,
        )
        return

    game = games[-1]

    if user.id in game.owner:
        game.translate = True
        await send_async(
            game,
            text=_("Enabled multi-translations. " "Disable with /disable_translations"),
        )
    else:
        await send_async(
            game,
            text=_("Only the game creator ({name}) and admin can do that.").format(
                name=game.starter.first_name
            ),
            reply_to_message_id=update.message.message_id,
        )

    return


@user_locale
async def disable_translations(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for the /disable_translations command"""
    chat = update.message.chat
    user = update.message.from_user
    games = gm.chatid_games.get(chat.id)

    if not games:
        await send_async(
            chat,
            text=_("There is no running game in this chat."),
            message_thread_id=update.message.message_thread_id,
        )
        return

    game = games[-1]

    if user.id in game.owner:
        game.translate = False
        await send_async(
            game,
            text=_(
                "Disabled multi-translations. "
                "Enable them again with "
                "/enable_translations"
            ),
        )
    else:
        await send_async(
            game,
            text=_("Only the game creator ({name}) and admin can do that.").format(
                name=game.starter.first_name
            ),
            reply_to_message_id=update.message.message_id,
        )

    return


@game_locales
@user_locale
async def skip_player(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for the /skip command"""
    chat = update.message.chat
    user = update.message.from_user

    player = gm.player_for_user_in_chat(user, chat)
    if not player:
        await send_async(
            chat,
            text=_("You are not playing in a game in this chat."),
            message_thread_id=update.message.message_thread_id,
        )
        return

    game = player.game
    skipped_player = game.current_player

    started = skipped_player.turn_started
    now = datetime.now()
    delta = (now - started).seconds

    # You can't skip if the current player still has time left
    # You can skip yourself even if you have time left (you'll still draw)
    if delta < skipped_player.waiting_time and player != skipped_player:
        n = skipped_player.waiting_time - delta
        await send_async(
            game,
            text=_("Please wait {time} second", "Please wait {time} seconds", n).format(
                time=n
            ),
            reply_to_message_id=update.message.message_id,
        )
    else:
        await do_skip(context, player)


@game_locales
@user_locale
async def reply_to_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handler for inline queries.
    Builds the result list for inline queries and answers to the client.
    """
    results = []
    switch = None

    try:
        user = update.inline_query.from_user
        user_id = user.id
        players = gm.userid_players[user_id]
        player = gm.userid_current[user_id]
        game = player.game
    except KeyError:
        add_no_game(results)
    else:

        # The game has not started.
        # The creator may change the game mode, other users just get a "game has not started" message.
        if not game.started:
            if user_is_creator(user, game):
                add_mode_classic(results)
                add_mode_fast(results)
                add_mode_wild(results)
                add_mode_text(results)
                add_mode_sete(results)
            else:
                add_not_started(results)

        elif user_id == game.current_player.user.id:
            if game.choosing_color:
                add_choose_color(results, game)
                add_other_cards(player, results, game)
            elif game.choosing_player:
                add_choose_player(player.user.id, results, game)
            else:
                if not player.drew:
                    add_draw(player, results)

                else:
                    add_pass(results, game)

                if game.last_card.special == c.DRAW_FOUR and game.draw_counter:
                    add_call_bluff(results, game)

                playable = player.playable_cards()
                added_ids = []  # Duplicates are not allowed

                for card in sorted(player.cards):
                    add_card(
                        game,
                        card,
                        results,
                        can_play=(card in playable and str(card) not in added_ids),
                    )
                    added_ids.append(str(card))

                add_gameinfo(game, results)

        else:
            for card in sorted(player.cards):
                add_card(game, card, results, can_play=False)

        for result in results:
            result.id += ":%d" % player.anti_cheat

        if players and game and len(players) > 1:
            switch = _("Current game: {game}").format(game=game.chat.title)

    await answer_async(
        context,
        update.inline_query.id,
        results,
        cache_time=0,
        switch_pm_text=switch,
        switch_pm_parameter="select",
    )


@game_locales
@user_locale
async def process_result(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handler for chosen inline results.
    Checks the players actions and acts accordingly.
    """
    try:
        user = update.chosen_inline_result.from_user
        player = gm.userid_current[user.id]
        game = player.game
        result_id = update.chosen_inline_result.result_id
        chat = game.chat
    except (KeyError, AttributeError):
        return

    logger.debug("Selected result: %s", result_id)

    result_id, anti_cheat = result_id.split(":")
    last_anti_cheat = player.anti_cheat
    player.anti_cheat += 1
    if result_id in ("hand", "gameinfo", "nogame"):
        return
    elif result_id.startswith("mode_"):
        # First 5 characters are 'mode_', the rest is the gamemode.
        mode = result_id[5:]
        game.set_mode(mode)
        logger.info("Gamemode changed to %s", mode)
        await send_async(game, text=__("Gamemode changed to {mode}".format(mode=mode)))
        return
    elif len(result_id) == 36:  # UUID result
        return
    elif int(anti_cheat) != last_anti_cheat:
        await send_async(
            game,
            text=__("Cheat attempt by {name}", multi=game.translate).format(
                name=display_name(player.user)
            ),
        )
        return
    elif result_id == "call_bluff":
        await reset_waiting_time(context, player)
        await do_call_bluff(context, player)
    elif "7" in result_id and game.mode == "7-0" and "player" not in result_id:
        game.choosing_player = True
        await send_async(game, text="Please choose a player to switch cards")
        remove_cards(player, result_id)
    elif "0" in result_id and game.mode == "7-0" and "player" not in result_id:
        await reset_waiting_time(context, player)
        await do_play_card(context, player, result_id)
        b = {a: i.cards for a, i in enumerate(game.players)}
        for a, i in enumerate(game.players, start=1):
            i.cards = b.get(a, b[0])
    elif result_id == "draw":
        await reset_waiting_time(context, player)
        await do_draw(context, player)
    elif result_id == "pass":
        game.turn()
    elif "player" in result_id:
        n = result_id[7:]
        for a, i in enumerate(game.players):
            if a == int(n):
                v = i.user.id
        pi = gm.userid_current[v]
        pq = pi.cards
        pn = player.cards
        pi.cards = pn
        player.cards = pq
        await subport(context, player, pi)
    elif result_id in c.COLORS:
        game.choose_color(result_id)
    else:
        await reset_waiting_time(context, player)
        await do_play_card(context, player, result_id)

    if game_is_running(game):
        nextplayer_message = __("Next player: {name}", multi=game.translate).format(
            name=display_name(game.current_player.user)
        )
        choice = [
            [
                InlineKeyboardButton(
                    text=_("Make your choice!"), switch_inline_query_current_chat=""
                )
            ]
        ]
        await send_async(
            game,
            text=nextplayer_message,
            reply_markup=InlineKeyboardMarkup(choice),
        )
        start_player_countdown(context, game)


async def reset_waiting_time(context, player):
    """Resets waiting time for a player and sends a notice to the group"""

    if player.waiting_time < WAITING_TIME:
        player.waiting_time = WAITING_TIME
        await send_async(
            player.game.thread_id,
            text=__(
                "Waiting time for {name} has been reset to {time} " "seconds",
                multi=player.game.translate,
            ).format(name=display_name(player.user), time=WAITING_TIME),
        )


# Add all handlers to the application and run the bot
application.add_handler(InlineQueryHandler(reply_to_query))
application.add_handler(ChosenInlineResultHandler(process_result))
application.add_handler(CallbackQueryHandler(select_game))
application.add_handler(CommandHandler("start", start_game))
application.add_handler(CommandHandler("new", new_game))
application.add_handler(CommandHandler("kill", kill_game))
application.add_handler(CommandHandler("join", join_game))
application.add_handler(CommandHandler("leave", leave_game))
application.add_handler(CommandHandler("kick", kick_player))
application.add_handler(CommandHandler("open", open_game))
application.add_handler(CommandHandler("close", close_game))
application.add_handler(CommandHandler("enable_translations", enable_translations))
application.add_handler(CommandHandler("disable_translations", disable_translations))
application.add_handler(CommandHandler("skip", skip_player))
application.add_handler(CommandHandler("notify_me", notify_me))
simple_commands.register()
settings.register()
application.add_handler(
    MessageHandler(filters.StatusUpdate.LEFT_CHAT_MEMBER, status_update)
)
application.add_error_handler(error)

# start the bot
application.run_polling()
