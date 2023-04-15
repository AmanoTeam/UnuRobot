import pyrogram
from pyrogram import Client, filters
from pyrogram.types import Message

from config import API_HASH, API_ID, BOT_TOKEN, WORKERS

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
    games[m.chat.id] = UnoGame()

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

    # Add the player to the game
    game.add_player(m.from_user)

    # Send the game's current state to the chat
    await m.reply_text(game.state())


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

    # Start the game
    game.start_game()

    # Send the game's current state to the chat
    await m.reply_text(game.state())


# Handler for regular messages
@app.on_message(filters.text)
async def text_handler(c: Client, m: Message):
    try:
        game = games[m.chat.id]
    except KeyError:
        return

    # Ignore messages that are not commands or player moves
    if not m.text.startswith("/") and m.text.isdigit():
        # Try to play the card the player chose
        result = game.play_card(int(m.text))

        # Send the game's current state to the chat
        await m.reply_text(result + "\n\n" + game.state())
