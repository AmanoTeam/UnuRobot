import logging

from telegram.ext import ContextTypes

import card as c
from config import MIN_FAST_TURN_TIME, TIME_REMOVAL_AFTER_SKIP
from errors import DeckEmptyError, NotEnoughPlayersError
from internationalization import __
from shared_vars import gm
from user_setting import UserSetting
from utils import display_name, game_is_running, send_async

logger = logging.getLogger(__name__)


class Countdown:
    player = None
    job_queue = None

    def __init__(self, player, job_queue):
        self.player = player
        self.job_queue = job_queue


# TODO do_skip() could get executed in another thread (it can be a job), so it looks like it can't use game.translate?
async def do_skip(context: ContextTypes.DEFAULT_TYPE, player):
    game = player.game
    chat = game.chat
    skipped_player = game.current_player
    next_player = game.current_player.next
    job_queue = context.job_queue

    if skipped_player.waiting_time > 0:
        skipped_player.anti_cheat += 1
        skipped_player.waiting_time -= TIME_REMOVAL_AFTER_SKIP
        if skipped_player.waiting_time < 0:
            skipped_player.waiting_time = 0

        try:
            skipped_player.draw()
        except DeckEmptyError:
            pass

        n = skipped_player.waiting_time
        await send_async(
            game,
            text=__(
                "Waiting time to skip this player has "
                "been reduced to {time} seconds.\n"
                "Next player: {name}",
                multi=game.translate,
            ).format(time=n, name=display_name(next_player.user)),
        )
        logger.info("%s was skipped!", display_name(player.user))
        game.turn()
        if job_queue:
            start_player_countdown(context, game)

    else:
        try:
            gm.leave_game(skipped_player.user, chat)
            await send_async(
                game,
                text=__(
                    "{name1} ran out of time "
                    "and has been removed from the game!\n"
                    "Next player: {name2}",
                    multi=game.translate,
                ).format(
                    name1=display_name(skipped_player.user),
                    name2=display_name(next_player.user),
                ),
            )
            logger.info("%s was skipped!", display_name(player.user))
            if job_queue:
                start_player_countdown(context, game)

        except NotEnoughPlayersError:
            await send_async(
                game,
                text=__(
                    "{name} ran out of time "
                    "and has been removed from the game!\n"
                    "The game ended.",
                    multi=game.translate,
                ).format(name=display_name(skipped_player.user)),
            )

            gm.end_game(chat, skipped_player.user)


def remove_cards(player, result_id):
    card = c.from_str(result_id)
    player.rm(card)


async def subport(context: ContextTypes.DEFAULT_TYPE, player, pi):
    game = player.game
    user = player.user

    us = UserSetting.get(id=user.id)
    if not us:
        us = UserSetting(id=user.id)

    if us.stats:
        us.cards_played += 1

    await verifi(context, player)
    await verifi(context, pi)

    game.turn()


async def verifi(context: ContextTypes.DEFAULT_TYPE, player):
    game = player.game
    chat = game.chat
    user = player.user

    us = UserSetting.get(id=user.id)
    if not us:
        us = UserSetting(id=user.id)

    if len(player.cards) == 1:
        await send_async(game, text="UNO!")

    if len(player.cards) == 0:
        await send_async(
            game,
            text=__("{name} won!", multi=game.translate).format(name=user.first_name),
        )

        if us.stats:
            us.games_played += 1

            if game.players_won == 0:
                us.first_places += 1

        game.players_won += 1

        try:
            gm.leave_game(user, chat)
        except NotEnoughPlayersError:
            await send_async(game, text=__("Game ended!", multi=game.translate))

            us2 = UserSetting.get(id=game.current_player.user.id)
            if us2 and us2.stats:
                us2.games_played += 1

            gm.end_game(chat, user)


async def do_play_card(context: ContextTypes.DEFAULT_TYPE, player, result_id):
    """Plays the selected card and sends an update to the group if needed"""
    card = c.from_str(result_id)
    player.play(card)
    game = player.game
    chat = game.chat
    user = player.user

    us = UserSetting.get(id=user.id)
    if not us:
        us = UserSetting(id=user.id)

    if us.stats:
        us.cards_played += 1

    if game.choosing_color:
        await send_async(game, text=__("Please choose a color", multi=game.translate))

    if len(player.cards) == 1:
        await send_async(game, text="UNO!")

    if len(player.cards) == 0:
        await send_async(
            game,
            text=__("{name} won!", multi=game.translate).format(name=user.first_name),
        )

        if us.stats:
            us.games_played += 1

            if game.players_won == 0:
                us.first_places += 1

        game.players_won += 1

        try:
            gm.leave_game(user, chat)
        except NotEnoughPlayersError:
            await send_async(game, text=__("Game ended!", multi=game.translate))

            us2 = UserSetting.get(id=game.current_player.user.id)
            if us2 and us2.stats:
                us2.games_played += 1

            gm.end_game(chat, user)


async def do_draw(context: ContextTypes.DEFAULT_TYPE, player):
    """Does the drawing"""
    game = player.game
    chat = game.chat
    draw_counter_before = game.draw_counter

    try:
        player.draw()
    except DeckEmptyError:
        await send_async(
            game,
            text=__("There are no more cards in the deck.", multi=game.translate),
        )

    if (
        game.last_card.value == c.DRAW_TWO or game.last_card.special == c.DRAW_FOUR
    ) and draw_counter_before > 0:
        game.turn()


async def do_call_bluff(context: ContextTypes.DEFAULT_TYPE, player):
    """Handles the bluff calling"""
    game = player.game
    chat = game.chat

    if player.prev.bluffing:
        await send_async(
            game,
            text=__(
                "Bluff called! Giving 4 cards to {name}", multi=game.translate
            ).format(name=player.prev.user.first_name),
        )

        try:
            player.prev.draw()
        except DeckEmptyError:
            await send_async(
                game,
                text=__("There are no more cards in the deck.", multi=game.translate),
            )

    else:
        game.draw_counter += 2
        await send_async(
            game,
            text=__(
                "{name1} didn't bluff! Giving 6 cards to {name2}", multi=game.translate
            ).format(name1=player.prev.user.first_name, name2=player.user.first_name),
        )
        try:
            player.draw()
        except DeckEmptyError:
            await send_async(
                game,
                text=__("There are no more cards in the deck.", multi=game.translate),
            )

    game.turn()


def start_player_countdown(context: ContextTypes.DEFAULT_TYPE, game):
    player = game.current_player
    time = player.waiting_time

    time = max(time, MIN_FAST_TURN_TIME)

    if game.mode == "fast":
        if game.job:
            game.job.schedule_removal()

        job = context.job_queue.run_once(
            # lambda x,y: do_skip(context, player),
            skip_job,
            time,
            data=Countdown(player, context.job_queue),
        )

        logger.info(
            "Started countdown for player: %s. %s seconds.",
            display_name(player.user),
            time,
        )
        player.game.job = job


async def skip_job(context: ContextTypes.DEFAULT_TYPE):
    player = context.job.data.player
    game = player.game
    if game_is_running(game):
        await do_skip(context, player)
