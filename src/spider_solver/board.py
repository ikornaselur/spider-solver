"""A game board

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

from enum import Enum
from typing import NamedTuple, Optional, Self, TypeAlias


class SpiderException(Exception):
    pass


class IllegalMove(SpiderException):
    pass


class CardNotFound(SpiderException):
    pass


class Card:
    num: int  # The value of the card from 1 to 13

    # Position metadata to identify duplicates. If not set, it could be in a
    # stack instead of the main board
    row: Optional[int]
    col: Optional[int]

    def __init__(
        self, num: int, row: Optional[int] = None, col: Optional[int] = None
    ) -> None:
        self.num = num
        self.row = row
        self.col = col

    @property
    def value(self) -> str:
        match self.num:
            case 1:
                return "A"
            case 10:
                return "0"  # Single width values for all cards
            case 11:
                return "J"
            case 12:
                return "D"
            case 13:
                return "K"
            case _:
                return str(self.num)

    @property
    def match(self) -> int:
        """The value that needs to match with this card

        The king will return the value 0, which means it can match by itself
        """
        return (13 - self.num) or 13

    @property
    def pos(self) -> str:
        if self.row is None or self.col is None:
            return "In stack"

        match self.row:
            case 0:
                row = "1st"
            case 1:
                row = "2nd"
            case 2:
                row = "3rd"
            case _:
                row = f"{self.row + 1}th"
        match self.col:
            case 0:
                col = "1st"
            case 1:
                col = "2nd"
            case 2:
                col = "3rd"
            case _:
                col = f"{self.col + 1}th"

        return f"On board {row} row, {col} card"

    def __repr__(self) -> str:
        return f"<Card {self.value}: {self.pos}>"


class MoveType(Enum):
    BoardMatch = "BoardMatch"
    BoardStackMatch = "BoardStackMatch"
    StackMatch = "StackMatch"


# The number of draws required from the stack
Draws: TypeAlias = int
Move: TypeAlias = tuple[MoveType, Draws, tuple[Card, ...]]


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

    def draw(self, count: int = 1) -> Card:
        """Draw the next card and return what card is now at the top"""
        self.idx = (self.idx + count) % len(self.cards)

        return self.peek

    @property
    def peek(self) -> Card:
        """Peek at the top card without drawing a new one"""
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

    def get_card_at_draws(self, draws: int) -> Card:
        """Return the card that would be at the top after this many draws"""
        return self.cards[(self.idx + draws) % len(self.cards)]

    def num_in_stack(self, num: int) -> list[int]:
        """Return how many draws would be required to get to the number in the stack

        If the card is visible as the previous card, it will be indicated as
        -1, to differentiate between the left and right visible cards
        # XXX: Is this a good idea?
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
            if card.num == num:
                draws_for_num.append(idx)

        return draws_for_num

    def get_stack_moves(self) -> set[Move]:
        moves = set()
        # Check for any pairs in the stack
        for idx, (left, right) in enumerate(zip(self.cards, self.cards[1:])):
            if right.num == 13:
                moves.add(
                    (
                        MoveType.StackMatch,
                        (idx + 1 - self.idx) % len(self.cards),
                        (right,),
                    )
                )
            elif left.match == right.num:
                moves.add(
                    (
                        MoveType.StackMatch,
                        (idx + 1 - self.idx) % len(self.cards),
                        (left, right),
                    )
                )
        return moves

    def __repr__(self) -> str:
        cards = [
            str(card.num) for card in self.cards[self.idx :] + self.cards[: self.idx]
        ]
        return f"<Stack {' '.join(cards)}>"


class Edges(NamedTuple):
    left: Optional[Card]
    right: Optional[Card]

    def __len__(self) -> int:
        return 1 if self.left else 0 + 1 if self.right else 0


class Board:
    stack: Stack
    cards: dict[Card, Edges]
    root_card: Card
    moves: int

    def __init__(self, rows: list[list[int]], stack: list[int]) -> None:
        if len(rows) != 7:
            raise ValueError("Exactly 7 rows of cards are required")
        if any(len(row) != idx + 1 for idx, row in enumerate(rows)):
            raise ValueError(
                "Number of cards per row needs to match the 1-indexed row number"
            )

        self.moves = 0
        self.cards = {}

        # Keep track of references to the cards from the row/column tuple to create the edges
        row_to_card_map: dict[tuple[int, int], Card] = {}

        for row_idx, row in enumerate(rows):
            for num_idx, num in enumerate(row):
                card = Card(num, row=row_idx, col=num_idx)
                self.cards[card] = Edges(None, None)
                row_to_card_map[(row_idx, num_idx)] = card

                if row_idx == 0:
                    # No cards above the first row
                    self.root_card = card
                if num_idx != 0:
                    # All numbers, except the first, will have a parent on the left
                    left_parent = row_to_card_map[(row_idx - 1, num_idx - 1)]
                    self.cards[left_parent] = Edges(self.cards[left_parent].left, card)
                if num_idx != len(row) - 1:
                    # All numbers, except last, will have a parent on the right
                    right_parent = row_to_card_map[(row_idx - 1, num_idx)]
                    self.cards[right_parent] = Edges(
                        card, self.cards[right_parent].right
                    )

        self.stack = Stack.from_ints(stack)

    @property
    def leaves(self) -> set[Card]:
        return set(card for card, edges in self.cards.items() if len(edges) == 0)

    def get_moves(self) -> set[Move]:
        """Calculate all moves that are possible in the current state

        The moves could be to match either two cards from the board itself, or,
        to match a card from the board with one from the stack.

        There could also be moves to match two cards in a row within the stack.

        The possible moves that require the stack indicate how many draws of
        the stack are required.

        If there are no moves possible, then the list of moves will be empty

        A move is a 3-tuple of (Move type, number of draws required from the
        stack, tuple of the cards to match)
        The tuple of cards can be a one tuple, only if it's a king.
        """
        moves = set()

        # Check for any matches on the table itself
        leaves = self.leaves
        for leaf in leaves:
            for match in (
                pot_match for pot_match in leaves if pot_match.match == leaf.num
            ):
                if leaf.num > match.num:
                    leaf, match = match, leaf
                if leaf == match:
                    # It's a king
                    moves.add((MoveType.BoardMatch, 0, (leaf,)))
                else:
                    moves.add((MoveType.BoardMatch, 0, (leaf, match)))

        # Check for any moves that require the stack
        for leaf in leaves:
            if not (idxs := self.stack.num_in_stack(leaf.match)):
                continue
            for idx in idxs:
                moves.add(
                    (
                        MoveType.BoardStackMatch,
                        max(
                            idx, 0
                        ),  # Left side of visible stack card is -1, no need to draw
                        (leaf, self.stack.get_card_at_draws(idx)),
                    )
                )

        # Check for any moves that match in the stack
        moves.update(self.stack.get_stack_moves())

        return moves

    def play_move(self, move: Move) -> int:
        """Play a move and return the current number of moves the board is at"""
        move_type, draws, cards = move

        if draws:
            self.stack.draw(draws)
            self.moves += draws

        match (move_type, cards):
            case (MoveType.BoardMatch, (left, right)):
                # Find the cards and ensure they can be moved
                if left not in self.cards or right not in cards:
                    raise CardNotFound()
                if self.cards[left] or self.cards[right]:
                    raise IllegalMove("Cards are blocked by other cards")

                # Remove blocks from cards above
                for card in self.cards:
                    if left in (parent := self.cards[card]):
                        if parent.left == left:
                            self.cards[card] = Edges(None, parent.right)
                        elif parent.right == left:
                            self.cards[card] = Edges(parent.left, None)

                    if right in (parent := self.cards[card]):
                        if parent.left == right:
                            self.cards[card] = Edges(None, parent.right)
                        elif parent.right == right:
                            self.cards[card] = Edges(parent.left, None)

                # Remove the cards
                del self.cards[left]
                del self.cards[right]
            case (MoveType.BoardMatch, (king,)):
                # Find the cards and ensure they can be moved
                if king not in self.cards:
                    raise CardNotFound()
                if self.cards[king]:
                    raise IllegalMove("Card is blocked by other cards")

                # Remove blocks from cards above
                for card in self.cards:
                    if king in (parent := self.cards[card]):
                        if parent.left == king:
                            self.cards[card] = Edges(None, parent.right)
                        elif parent.right == king:
                            self.cards[card] = Edges(parent.left, None)

                # Remove the cards
                del self.cards[king]
            case MoveType.BoardStackMatch:
                pass
            case MoveType.StackMatch:
                pass

        self.moves += 1

        return self.moves

    def __repr__(self) -> str:
        cards = [self.root_card]

        indent = 7
        lines = []
        while any(card is not None for card in cards):
            next_cards = []
            row = " " * indent
            indent -= 1
            for card in cards:
                if card:
                    row += f"{card.value} "
                    next_cards.append(self.cards[card].left)
                else:
                    row += "  "
                    next_cards.append(None)
            # Add the far right based on last card
            if cards[-1]:
                next_cards.append(self.cards[cards[-1]].right)

            lines.append(row.rstrip())
            cards = next_cards

        # Show the stack in the top line, right corner
        left_card = self.stack.prev
        right_card = self.stack.peek

        lines[0] += f" {left_card.value if left_card else ' '} {right_card.value}"

        return "\n".join(lines)

    def __str__(self) -> str:
        return f"<Board ({self.moves} moves)>"
