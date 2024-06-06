from hydrogram import Client


games = {}
player_game = {}

API_ID = ''
API_HASH = ''

#--- Telegram config ---

bot = Client("bot", api_id=API_ID, api_hash=API_HASH, plugins=dict(root="plugins"))
