import pyrogram
from pyrogram import Client, filters
from pyrogram.types import (
    ChosenInlineResult,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InlineQuery,
    InlineQueryResultArticle,
    InputTextMessageContent,
    Message,
)

from config import API_HASH, API_ID, BOT_TOKEN, MIN_PLAYERS, WORKERS

from .core import UnoGame

# Create a new Pyrogram client instance
app = pyrogram.Client(
    "unu", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN, workers=WORKERS
)


games: dict[int, UnoGame] = {}


# Handler for the "/start" command
@app.on_message(filters.command("start"))
async def start_handler(c: Client, m: Message):
    await m.reply_text("Welcome to UNO! Use /play to start a new game.")


# Handler for the "/new" command
@app.on_message(filters.command("new"))
async def new_handler(c: Client, m: Message):
    if m.chat.id in games:
        await m.reply_text("There is already a game in this chat. Join it with /join.")
        return

    # Start a new game
    games[m.chat.id] = UnoGame(m.chat)

    # Add the player to the game
    await m.reply_text("Started a new game. Use /join to join and /play to start.")


# Handler for the "/join" command
@app.on_message(filters.command("join"))
async def join_handler(c: Client, m: Message):
    try:
        game = games[m.chat.id]
    except KeyError:
        await m.reply_text(
            "There is no game in this chat. Use /new to start a new game."
        )
        return

    for player in game.players:
        if player.player.id == m.from_user.id:
            await m.reply_text("You are already in the game.")
            return

    # Add the player to the game
    game.add_player(m.from_user)

    # Send the game's current state to the chat
    await m.reply_text(
        "Joined the game. Use /play to start.\n\n" + game.get_players_list()
    )


# Handler for the "/skip" command
@app.on_message(filters.command("skip"))
async def skip_handler(c: Client, m: Message):
    try:
        game = games[m.chat.id]
    except KeyError:
        await m.reply_text(
            "There is no game in this chat. Use /new to start a new game."
        )
        return

    # Skip the current player
    game.next_player()

    # Send the game's current state to the chat
    await m.reply_text(game.state())


# Handler for the "/leave" command
@app.on_message(filters.command("leave"))
async def leave_handler(c: Client, m: Message):
    try:
        game = games[m.chat.id]
    except KeyError:
        await m.reply_text(
            "There is no game in this chat. Use /new to start a new game."
        )
        return

    # Remove the player from the game
    game.remove_player(m.from_user)

    # Send the game's current state to the chat
    await m.reply_text("Alright, no problem.\n\n" + game.state())


# Handler for the "/play" command
@app.on_message(filters.command("play"))
async def play_handler(c: Client, m: Message):
    try:
        game = games[m.chat.id]
    except KeyError:
        await m.reply_text(
            "There is no game in this chat. Use /new to start a new game."
        )
        return

    if game.started:
        await m.reply_text("The game has already started.")
        return

    if len(game.players) < MIN_PLAYERS:
        await m.reply_text(
            f"You need at least {MIN_PLAYERS} players to start the game."
        )
        return

    # Start the game
    game.start_game()

    # Send the game's current state to the chat
    await m.reply_text(
        game.state(),
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "Play a card",
                        switch_inline_query_current_chat="",
                    )
                ]
            ]
        ),
    )


# List player cards in inline mode
@app.on_inline_query()
async def inline_handler(c: Client, m: InlineQuery):
    # Get the first game a player is in
    current_game = None
    current_player = None

    for game in games.values():
        for player in game.players:
            if player.player.id == m.from_user.id:
                current_game = game
                current_player = player
                break

    if current_game is None or current_player is None:
        await m.answer(
            results=[
                InlineQueryResultArticle(
                    id="not_in_game",
                    title="Not in a game",
                    input_message_content=InputTextMessageContent(
                        "You are not in a game."
                    ),
                )
            ],
            cache_time=0,
            is_personal=True,
        )
        return

    # Get the player's cards
    cards = current_player.cards

    # Create a list of results
    results = [
        InlineQueryResultArticle(
            id="pass",
            title="Pass",
            input_message_content=InputTextMessageContent("Pass"),
        ),
        InlineQueryResultArticle(
            id="draw",
            title="Draw a card",
            input_message_content=InputTextMessageContent("Draw a card"),
        ),
    ]

    results.extend(
        InlineQueryResultArticle(
            id=f"{i}",
            title=f"{card}",
            input_message_content=InputTextMessageContent(f"Played {card}"),
        )
        for i, card in enumerate(cards)
    )
    # Send the results to the user
    await m.answer(results=results, cache_time=0, is_personal=True)


@app.on_chosen_inline_result(
    filters.create(lambda _, __, query: query.result_id in ["pass", "draw"])
)
async def pass_or_draw(c: Client, m: ChosenInlineResult):
    # Get the first game a player is in
    current_game = None
    current_player = None

    for game in games.values():
        for player in game.players:
            if player.player.id == m.from_user.id:
                current_game = game
                current_player = player
                break

    if current_game is None or current_player is None:
        return

    if m.result_id == "pass":
        current_game.next_player()
    elif m.result_id == "draw":
        current_game.draw_card()

    await c.send_message(
        chat_id=current_game.chat.id,
        text=current_game.state(),
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("Play a card", switch_inline_query_current_chat="")]]
        ),
    )


# Handler for inline query results
@app.on_chosen_inline_result(
    filters.create(lambda _, __, query: query.result_id.isdigit())
)
async def chosen_inline_handler(c: Client, m: ChosenInlineResult):
    # Get the first game a player is in
    current_game = None
    current_player = None

    for game in games.values():
        for player in game.players:
            if player.player.id == m.from_user.id:
                current_game = game
                current_player = player
                break

    if current_game is None or current_player is None:
        return

    # Play the card
    if current_game.play_card(int(m.result_id)):
        current_game.next_player()

        await c.send_message(
            chat_id=current_game.chat.id,
            text=current_game.state(),
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "Play a card", switch_inline_query_current_chat=""
                        )
                    ]
                ]
            ),
        )
    else:
        await c.send_message(
            chat_id=current_game.chat.id,
            text="You can't play that card. Try another one.",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "Play a card", switch_inline_query_current_chat=""
                        )
                    ]
                ]
            ),
        )
