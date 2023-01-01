""" A game board

A game board is a Spider Solitare board that has 7 rows, with the top row
having one card and bottom row having 7 cards.

A card is going to be blocked by the two cards below it, in a pyramid fashion,
creating sort of a one directional graph where only the leaves (that don't
point to any other cards) can be removed.

While this is techincally a graph, each node will only have 0, 1 or 2 one way
edges to other nodes. A node may have 0, 1 or 2 one direction edges from other
nodes pointing at it.
"""
from __future__ import annotations

from typing import Self


class Board:
    stack: Stack
    cards: dict[Card, set[Card]]

    def __init__(self, rows: list[list[int]], stack: list[int]) -> None:
        if len(rows) != 7:
            raise ValueError("Exactly 7 rows of cards are required")
        if any(len(row) != idx + 1 for idx, row in enumerate(rows)):
            raise ValueError(
                "Number of cards per row needs to match the 1-indexed row number"
            )

        self.cards = {}

        # Keep track of references to the cards from the row/column tuple to create the edges
        row_to_card_map: dict[tuple[int, int], Card] = {}

        for row_idx, row in enumerate(rows):
            for num_idx, num in enumerate(row):
                card = Card(num)
                self.cards[card] = set()
                row_to_card_map[(row_idx, num_idx)] = card

                if row_idx == 0:
                    # No cards above the first row
                    continue
                if num_idx != 0:
                    # All numbers, except the first, will have a parent on the left
                    left_parent = row_to_card_map[(row_idx - 1, num_idx - 1)]
                    self.cards[left_parent].add(card)
                if num_idx != len(row) - 1:
                    # All numbers, except last, will have a parent on the right
                    right_parent = row_to_card_map[(row_idx - 1, num_idx)]
                    self.cards[right_parent].add(card)

        self.stack = Stack.from_ints(stack)

    @property
    def leafs(self) -> set[Card]:
        return set(card for card, edges in self.cards.items() if len(edges) == 0)


class Stack:
    """A stack of cards that can be drawn from

    An index to the current card on the top of the stack is kept, rather than
    changing the order itself
    """

    cards: list[Card]
    idx: int

    def __init__(self, cards: list[Card]) -> None:
        self.cards = cards
        self.idx = 0

    @classmethod
    def from_ints(cls, cards: list[int]) -> Self:
        return cls([Card(num) for num in cards])

    def draw(self) -> Card:
        """Draw the next card and return what card is now at the top"""
        self.idx = (self.idx + 1) % len(self.cards)

        return self.peek()

    def peek(self) -> Card:
        """Peek at the top card without drawing a new one"""
        return self.cards[self.idx]

    def __repr__(self) -> str:
        cards = [
            str(card.num) for card in self.cards[self.idx :] + self.cards[: self.idx]
        ]
        return f"<Stack {' '.join(cards)}>"


class Card:
    num: int  # The value of the card from 1 to 13

    def __init__(self, num: int) -> None:
        self.num = num

    @property
    def value(self) -> str:
        match self.num:
            case 1:
                return "A"
            case 11:
                return "J"
            case 12:
                return "D"
            case 13:
                return "K"
            case _:
                return str(self.num)

    def __repr__(self) -> str:
        return f"<Card {self.value}>"
