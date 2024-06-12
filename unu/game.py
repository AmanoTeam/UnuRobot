import asyncio

from hydrogram.types import Chat, User, Message

from config import bot, timeout
from unu.deck import Deck


class Game:
    def __init__(self, chat: Chat, theme) -> None:
        self.chat = chat
        self.last_card = None
        self.last_card_2 = None
        self.next_player: User = None
        self.deck = Deck(theme)
        self.players = {}
        self.is_started = False
        self.draw = 0
        self.drawed = False
        self.chosen = None
        self.closed = False
        self.winner = True
        self.timer_task = None
        self.timer_duration = timeout
        self.message: Message = None

    def next(self):
        self.drawed = False
        indice = list(self.players.keys()).index(self.next_player.id)
        next_ind = (indice + 1) % len(self.players)
        next_key = list(self.players.keys())[next_ind]
        self.next_player = self.players[next_key]

        if self.timer_task:
            self.timer_task.cancel()

        self.timer_task = asyncio.create_task(self.start_timer())

    def start(self):
        self.is_started = True
        self.timer_task = asyncio.create_task(self.start_timer())

    def stop(self):
        if self.timer_task:
            self.timer_task.cancel()

    async def start_timer(self):
        await asyncio.sleep(self.timer_duration)
        await bot.send_message(
            self.chat.id, f"Time's up! {self.next_player.first_name} has been skipped."
        )
        self.next()
        await bot.send_message(self.chat.id, f"{self.next_player.first_name}'s turn.")
