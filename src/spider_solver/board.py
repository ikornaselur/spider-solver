""" A game board

A game board is a Spider Solitare board that has 7 rows, with the top row
having one card and bottom row having 7 cards.

A card is going to be blocked by the two cards below it, in a pyramid fashion,
creating sort of a binary tree where only the leaves can be removed.
"""
from __future__ import annotations

from typing import Optional, Self


class Board:
    card_root: Optional[Card]
    stack: Stack

    def __init__(self, card_root: Card, stack: Stack) -> None:
        self.card_root = card_root
        self.stack = stack

    @classmethod
    def from_ints(cls, rows: list[list[int]], stack: list[int]) -> Self:
        if len(rows) != 7:
            raise ValueError("Exactly 7 rows of cards are required")
        if any(len(row) != idx + 1 for idx, row in enumerate(rows)):
            raise ValueError(
                "Number of cards per row needs to match the 1-indexed row number"
            )

        carded_rows = []
        for row_num in range(len(rows)):
            carded_rows.append([Card(num) for num in rows[row_num]])
            if row_num == 0:
                continue

            for idx in range(len(carded_rows[row_num-1])):
                carded_rows[row_num-1][idx].set_lr(carded_rows[row_num][idx], carded_rows[row_num][idx+1])

        return cls(card_root=carded_rows[0][0], stack=Stack.from_ints(stack))


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
    """A game card, which can have up to two cards blocking it"""

    num: int  # The value of the card from 1 to 13
    parent: Optional[Card]
    left: Optional[Card]
    right: Optional[Card]

    def __init__(
        self,
        num: int,
        parent: Optional[Card] = None,
        left: Optional[Card] = None,
        right: Optional[Card] = None,
    ) -> None:
        self.num = num
        self.parent = parent
        self.set_left(left)
        self.set_right(right)

    def set_left(self, card: Optional[Card]) -> None:
        self.left = card
        if self.left:
            self.left.parent = self

    def set_right(self, card: Optional[Card]) -> None:
        self.right = card
        if self.right:
            self.right.parent = self

    def set_lr(self, left: Card, right: Card) -> None:
        self.set_left(left)
        self.set_right(right)

    @property
    def value(self) -> str:
        match self.num:
            case 11:
                return "J"
            case 12:
                return "D"
            case 13:
                return "K"
            case _:
                return str(self.num)

    def __repr__(self) -> str:
        left_val = self.left.value if self.left else "_"
        right_val = self.right.value if self.right else "_"
        return f"<Card {left_val}<-{self.value}->{right_val}>"
