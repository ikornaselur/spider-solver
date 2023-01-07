from __future__ import annotations

from collections.abc import Sequence
from typing import Optional, Union

from typing_extensions import Self

from spider_solver.card import Card
from spider_solver.exceptions import IllegalMove
from spider_solver.types import Move, MoveType


class Stack:
    """A stack of cards that can be drawn from

    An index to the current card on the top of the stack is kept, rather than
    changing the order itself
    """

    cards: list[Optional[Card]]
    idx: int

    def __init__(self, cards: list[Optional[Card]]) -> None:
        self.cards = cards
        self.cards.append(None)  # We cna draw past the last card
        self.idx = 0

    @classmethod
    def from_ints(cls, cards: list[int]) -> Self:
        return cls([Card(num) for num in cards])

    def draw(self, count: int = 1) -> Optional[Card]:
        """Draw the next card and return what card is now at the top"""
        self.idx = (self.idx + count) % len(self.cards)

        return self.peek

    @property
    def peek(self) -> Optional[Card]:
        """Peek at the top card without drawing a new one

        None if the stack is empty
        """
        if not self.cards:
            return None
        return self.cards[self.idx]

    @property
    def prev(self) -> Optional[Card]:
        """The previous card, if the top one is now being shown

        Two cards are shown at the same time in the Solitare, allowing the user
        to match two cards in a row from the stack.
        """
        if self.idx == 0:
            return None

        return self.cards[self.idx - 1]

    def get_card_at_draws(self, draws: int) -> Optional[Card]:
        """Return the card that would be at the top after this many draws"""
        return self.cards[(self.idx + draws) % len(self.cards)]

    def num_in_stack(self, num: int) -> list[int]:
        """Return how many draws would be required to get to the number in the stack

        If the card is visible as the previous card, it will be indicated as
        -1, to differentiate between the left and right visible cards
        # XXX: Is this a good idea?
        # INFO: It did work out in hte end, so I think it was a good idea?
        """
        if self.idx == 0:
            # Whole stack is just in order, only one visible card
            curr_order = self.cards[:]
        else:
            # We skip the card before current idx, as it is visible
            curr_order = self.cards[self.idx :] + self.cards[: self.idx - 1]

        draws_for_num = []
        if self.prev is not None and self.prev.num == num:
            draws_for_num.append(-1)
        for idx, card in enumerate(curr_order):
            if card is not None and card.num == num:
                draws_for_num.append(idx)

        return draws_for_num

    def get_stack_moves(self) -> set[Move]:
        moves = set()
        # Check for any pairs in the stack
        for idx, (left, right) in enumerate(zip(self.cards, self.cards[1:])):
            if right is not None and right.num == 13:
                moves.add(
                    (
                        MoveType.StackMatch,
                        (idx + 1 - self.idx) % len(self.cards),
                        (right,),
                    )
                )
            elif left is not None and right is not None and left.match == right.num:
                moves.add(
                    (
                        MoveType.StackMatch,
                        (idx + 1 - self.idx) % len(self.cards),
                        (left, right),
                    )
                )
        return moves

    def remove_cards(self, cards: Union[Card, Sequence[Card]]) -> None:
        """Remove a visible card from the stack"""
        if cards is None:
            raise IllegalMove("Can not remove the empty None slot at the back")
        if isinstance(cards, Card):
            cards = [cards]

        for card in cards:
            if self.prev is not card and self.peek is not card:
                raise IllegalMove(
                    "Unable to remove card, it's not visible from the stack"
                )

        for card in cards:
            if self.prev is card:
                # Shift the index back as we are removing a card prior to the current idx
                self.idx -= 1
            # if self.peek is card and self.idx:
            # We are removing the current card,

            self.cards.remove(card)

    def __repr__(self) -> str:
        cards = [
            str(card.num) if card else "X"
            for card in self.cards[self.idx :] + self.cards[: self.idx]
        ]
        return f"<Stack {' '.join(cards)}>"
