import random

from pyrogram.types import User

from .utils import color_name_to_emoji


class UnoCard:
    """This class represents a card in the game."""

    def __init__(self, color: str, number: int):
        self.color = color
        self.number = number

    def __repr__(self):
        return f"{color_name_to_emoji(self.color)} {self.number}"


class UnoPlayer:
    """This class holds the information about a player in the game."""

    def __init__(self, player: User):
        self.player = player
        self.cards: list[UnoCard] = []

    def add_cards(self, cards: list[UnoCard]):
        """Add the given cards to the player's hand."""

        self.cards.extend(cards)

    def get_card(self, index: int):
        """Get a card of a player at the given index."""

        return self.cards[index]

    def can_play_in_game(self, card: UnoCard, game: "UnoGame"):
        """Check if the player can play the given card in the given game."""

        if card.color == "Wild":
            return True

        if card.color == game.last_card.color:
            return True

        if card.number == game.last_card.number:
            return True

        return False


class UnoGame:
    def __init__(self):
        self.players: list[UnoPlayer] = []
        self.started = False
        self.deck: list[UnoCard] = []
        self.last_card: UnoCard = None
        self.current_player = 0
        self.direction = 1

        # fill the deck with cards
        self.deck = [
            UnoCard(color, number)
            for color in ["Red", "Blue", "Green", "Yellow"]
            for number in range(10)
        ]
        # add 4 wild cards
        self.deck.extend([UnoCard("Wild", 0) for _ in range(4)])
        random.shuffle(self.deck)

    def add_player(self, player: User):
        self.players.append(UnoPlayer(player))

    def distribute_cards(self):
        for player in self.players:
            player.add_cards(self.deck[:7])
            self.deck = self.deck[7:]

    def state(self):
        return (
            f"Current player: {self.players[self.current_player].player.first_name}\n"
            + f"Last card: {self.last_card}\n\n"
            + self.get_players_list()
        )

    def get_players_list(self):
        return "Players:\n" + "\n".join(
            f"{player.player.first_name} ({len(player.cards)} cards)"
            if player.cards
            else f"{player.player.first_name}"
            for player in self.players
        )

    def remove_player(self, player: User):
        for i, p in enumerate(self.players):
            if p.player.id == player.id:
                self.players.pop(i)
                break

    def next_player(self):
        self.current_player += self.direction

        if self.current_player >= len(self.players):
            self.current_player = 0
        elif self.current_player < 0:
            self.current_player = len(self.players) - 1

    def play_card(self, card_index: int):
        player = self.players[self.current_player]
        card = player.get_card(card_index)

        if player.can_play_in_game(card, self):
            player.cards.remove(card)
            self.last_card = card
            return "Played card."
        else:
            return "Invalid move."

    def get_random_card(self):
        return UnoCard(
            random.choice(["Red", "Blue", "Green", "Yellow"]), random.randint(0, 9)
        )

    def start_game(self):
        self.deck = [
            UnoCard(color, number)
            for color in ["Red", "Blue", "Green", "Yellow"]
            for number in range(10)
        ]

        random.shuffle(self.deck)

        self.current_player = 0
        self.direction = 1

        self.distribute_cards()

        self.last_card = self.get_random_card()

        self.started = True

        return self.state()
