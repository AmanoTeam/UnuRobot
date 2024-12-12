import os

from tortoise import Tortoise, connections, fields
from tortoise.backends.base.client import Capabilities
from tortoise.models import Model


class Chat(Model):
    id = fields.IntField(pk=True)
    theme = fields.CharField(max_length=255, default="classic")
    bluff = fields.BooleanField(default=True)
    seven = fields.BooleanField(default=False)
    one_win = fields.BooleanField(default=False)
    one_card = fields.BooleanField(default=False)
    lang = fields.CharField(max_length=255, default="en-US")
    auto_pin = fields.BooleanField(default=False)
    satack = fields.BooleanField(default=True)
    draw_one = fields.BooleanField(default=True)


class User(Model):
    id = fields.BigIntField(pk=True)
    placar = fields.BooleanField(default=False)
    wins = fields.IntField(default=0)
    matches = fields.IntField(default=0)
    cards = fields.IntField(default=0)
    sudo = fields.BooleanField(default=False)
    lang = fields.CharField(max_length=255, default="en-US")


class GameModel(Model):
    id = fields.IntField(pk=True)
    theme = fields.CharField(max_length=255)
    chat_id = fields.IntField(null=True)
    last_card = fields.JSONField(null=True)
    last_card_2 = fields.JSONField(null=True)
    next_player_id = fields.IntField(null=True)
    deck = fields.JSONField(null=True)
    players = fields.JSONField(null=True)
    is_started = fields.BooleanField(default=False)
    draw = fields.IntField(default=0)
    drawed = fields.BooleanField(default=False)
    chosen = fields.CharField(max_length=255, null=True)
    closed = fields.BooleanField(default=False)
    winner = fields.BooleanField(default=True)
    timer_duration = fields.IntField(default=30)
    message_id = fields.IntField(null=True)
    is_dev = fields.BooleanField(default=False)
    bluff = fields.BooleanField(default=False)


class GamePlayer(Model):
    player_id = fields.IntField()
    game_chat_id = fields.IntField()


async def connect_database():
    await Tortoise.init({
        "connections": {"bot_db": os.getenv("DATABASE_URL", "sqlite://database.sqlite")},
        "apps": {"bot": {"models": [__name__], "default_connection": "bot_db"}},
    })

    conn = connections.get("bot_db")
    conn.capabilities = Capabilities(
        "sqlite",
        daemon=False,
        requires_limit=True,
        inline_comment=True,
        support_for_update=False,
        support_update_limit_order_by=False,
    )

    # Generate the schema
    await Tortoise.generate_schemas()
