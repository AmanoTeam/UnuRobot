import random

from unu.card import cards


class Deck:
    def __init__(self, theme) -> None:
        self.theme = theme
        self.cards = [
            (color, value)
            for _ in range(2)
            for color in cards[theme]["CARDS"]["COLORS"]
            for value in cards[theme]["CARDS"]["VALUES"]
        ]
        self.cards += [
            ("x", car)
            for car in cards[theme]["CARDS"]["SPECIALS"]
            for _ in range(cards[theme]["CARDS"]["SPECIALS_INFO"][car][0])
        ]

    def shuffle(self):
        random.shuffle(self.cards)

    def draw(self, amount):
        return [self.cards.pop(0) for _ in range(amount) if self.cards]
