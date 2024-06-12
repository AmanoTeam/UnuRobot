from hydrogram import Client

games = {}
player_game = {}

timeout = 120
minimum_players = 2

sudoers = [123456789]

API_ID = ""
API_HASH = ""

# --- Telegram config ---

bot = Client("bot", api_id=API_ID, api_hash=API_HASH, plugins={"root": "unu.plugins"})
