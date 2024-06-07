from hydrogram.types import Chat, User

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
        self.chosen = None
        self.closed = False
        self.winner = True

    def next(self):
        if self.draw >= 0:
            indice = list(self.players.keys()).index(self.next_player.id)
            next_ind = (indice + 1) % len(self.players)
            next_key = list(self.players.keys())[next_ind]
            self.next_player = self.players[next_key]
