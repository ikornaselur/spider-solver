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

from collections import Counter
from collections.abc import Sequence
from enum import Enum
from typing import NamedTuple, Optional, Self, TypeAlias, Union


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
    def on_board(self) -> bool:
        """Whether the card is on the playing board or not

        If False, the card is in the stack
        """
        return self.row is not None and self.col is not None

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

    def __init__(
        self, rows: list[list[int]], stack: list[int], _validate: bool = True
    ) -> None:
        if _validate:
            # For testing..
            if len(rows) != 7:
                raise ValueError("Exactly 7 rows of cards are required")
            if any(len(row) != idx + 1 for idx, row in enumerate(rows)):
                raise ValueError(
                    "Number of cards per row needs to match the 1-indexed row number"
                )
            if sum(len(row) for row in rows) + len(stack) != 52:
                raise ValueError("Expected 52 cards")
            # Check counts of all 13 sorts is 4
            card_vals = Counter([num for row in rows for num in row] + stack)
            if len(card_vals) != 13:
                raise ValueError("Expected 13 sorts")
            if any(count != 4 for count in card_vals.values()):
                raise ValueError("Not all sorts are 4 counts")


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

        Some feeble optimisations:
            * If there is a removable king without drawing, it's the only move
            * If we have to draw to continue and there is a king on top of the
              stack, removing it is the only move
            * If any match can be done where it's the last two cards of their
              sort, then that's the only move
                - If they're on the table, just get it out of the way
                - If they're in the stack, only give them as the only option if
                  the only alternatives are to draw anyway
                - If removing cards locks other cards in the graph, it's not a
                  valid move! # TODO This
        """
        moves = set()

        # Get cards that only have 1 count left
        card_counts = Counter(
            [card.num for card in self.cards.keys()]
            + [card.num for card in self.stack.cards if card]
        )
        solo_cards = {key for key, val in card_counts.items() if val == 1}

        # Check for any matches on the table itself
        moves_on_table = False
        leaves = self.leaves
        for leaf in leaves:
            for match in (
                pot_match for pot_match in leaves if pot_match.match == leaf.num
            ):
                if leaf.num > match.num:
                    leaf, match = match, leaf
                if leaf is match:
                    # It's a king, we just return that as the only move!
                    return {(MoveType.BoardMatch, 0, (leaf,))}
                elif leaf.num in solo_cards:
                    # This is a part of a last pair, it's the only logical move
                    return {(MoveType.BoardMatch, 0, (leaf, match))}
                else:
                    moves.add((MoveType.BoardMatch, 0, (leaf, match)))
                    moves_on_table = True

        # Check for any moves that require the stack
        for leaf in leaves:
            if not (idxs := self.stack.num_in_stack(leaf.match)):
                continue
            for idx in idxs:
                if leaf.num in solo_cards and idx <= 0:
                    # We should get rid of it ASAP
                    stack_card = self.stack.get_card_at_draws(idx)
                    if stack_card is None:
                        raise SpiderException(
                            "Incorrectly matched the empty spot in the stack"
                        )
                    return {(MoveType.BoardStackMatch, max(idx, 0), (leaf, stack_card))}
                # Left side of visible stack card is -1, no need to draw, hence max()
                moves.add(
                    (
                        MoveType.BoardStackMatch,
                        max(idx, 0),
                        (leaf, self.stack.get_card_at_draws(idx)),
                    )
                )

        # Check for any moves that match in the stack
        stack_moves = self.stack.get_stack_moves()
        for move_type, draws, cards in stack_moves:
            if (
                draws == 0
                and (cards[0].num in solo_cards or cards[0].num == 13)
                and not moves_on_table
            ):
                # This stack move is a solo move, but we should only return it
                # IF there are no 0 draw moves already available
                return {(move_type, draws, cards)}
        moves.update(stack_moves)

        return moves

    def play_move(self, move: Move) -> int:
        """Play a move and return the current number of moves the board is at"""
        move_type, draws, cards = move

        if draws:
            self.stack.draw(draws)
            self.moves += draws

        # TODO: No need to use types, given that we can just check if cards are on board or stack
        match (move_type, cards):
            case (MoveType.BoardMatch, cards):
                self._remove_cards(cards)
            case (MoveType.BoardStackMatch, (board_card, stack_card)):
                if not board_card.on_board ^ stack_card.on_board:
                    raise SpiderException(
                        "Expected one card to be on board and other on stack"
                    )

                if not board_card.on_board:
                    # Flip them around to be correct
                    board_card, stack_card = stack_card, board_card

                if (
                    stack_card is not self.stack.peek
                    and stack_card is not self.stack.prev
                ):
                    raise IllegalMove("Unable to match a stack card that isn't visible")

                # Remove the stack card from the stack
                self.stack.remove_cards(stack_card)

                # Remove the board card from the board
                self._remove_cards(board_card)
            case (MoveType.StackMatch, cards):
                self.stack.remove_cards(cards)
            case _:
                raise IllegalMove("Unmatched move")

        self.moves += 1

        return self.moves

    def _remove_cards(self, cards_to_remove: Union[Card, Sequence[Card]]) -> None:
        if isinstance(cards_to_remove, Card):
            cards_to_remove = [cards_to_remove]

        # Validate
        for card in cards_to_remove:
            # Find the cards and ensure they can be moved
            if card not in self.cards:
                raise CardNotFound()
            if self.cards[card]:
                raise IllegalMove("Card is blocked by other cards")

        # Remove blocks from cards above
        for card_to_remove in cards_to_remove:
            for card in self.cards:
                if card_to_remove in (parent := self.cards[card]):
                    if parent.left is card_to_remove:
                        self.cards[card] = Edges(None, parent.right)
                    elif parent.right is card_to_remove:
                        self.cards[card] = Edges(parent.left, None)

            # Remove the cards
            del self.cards[card_to_remove]

    def __repr__(self) -> str:
        if not self.cards:
            return "Finished!"
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

        lines[
            0
        ] += f"  {left_card.value if left_card else ' '} {right_card.value if right_card else ' '}"

        return "\n".join(lines)

    def __str__(self) -> str:
        return f"<Board ({self.moves} moves)>"
