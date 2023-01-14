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

from collections import Counter, defaultdict
from collections.abc import Sequence
from typing import NamedTuple

from spider_solver.card import Card
from spider_solver.exceptions import CardNotFound, IllegalMove, SpiderException
from spider_solver.stack import Stack
from spider_solver.types import Move, MoveType


class Edges(NamedTuple):
    left: Card | None
    right: Card | None

    @property
    def edge_state(self) -> str:
        return f"{self.left.value if self.left else '_'}:{self.right.value if self.right else '_'}"

    def __len__(self) -> int:
        return 1 if self.left else 0 + 1 if self.right else 0


class Board:
    stack: Stack
    cards: dict[Card, Edges]
    root_card: Card
    moves: int
    blocked_by: defaultdict[Card, set[Card]]
    _optimise_blocked_by: bool

    def __init__(
        self,
        rows: list[list[int]],
        stack: list[int],
        _validate: bool = True,
        _optimise_blocked_by: bool = True,
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
            mis_match_counts = [key for key, val in card_vals.items() if val != 4]
            if any(mis_match_counts):
                raise ValueError(f"Not all sorts are 4 counts: {mis_match_counts}")

        self.moves = 0
        self.cards = {}
        self.blocked_by = defaultdict(set)

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

        self._optimise_blocked_by = _optimise_blocked_by
        if hasattr(self, "root_card"):
            # Special test case.. it's just easy like this
            self._walk(self.root_card)

        self.stack = Stack.from_ints(stack)

    def _walk(self, card: Card, seen: set[Card] | None = None) -> None:
        """Run through the card graph and make note of any cards that are blocked by others

        A card is considered blocked by another card if they would match each
        other and you can reach the lower card through the graph from the
        upper card. This means that if you have the following board:
            3
           2  5
          7 10 11
        Then the 3 is blocked by 10, but the 2 is not blocked by 11
        """
        if not self._optimise_blocked_by:
            return
        if seen is None:
            seen = set()

        for seen_card in seen:
            if card.match == seen_card.num:
                self.blocked_by[seen_card].add(card)

        if card.num < 13:
            seen.add(card)

        edges = self.cards[card]
        if edges.left is not None:
            self._walk(edges.left, seen.copy())
        if edges.right is not None:
            self._walk(edges.right, seen.copy())

    @property
    def leaves(self) -> set[Card]:
        return set(card for card, edges in self.cards.items() if len(edges) == 0)

    def get_card_at_row_col(self, row: int, col: int) -> Card | None:
        for card in self.cards:
            if card.row == row and card.col == col:
                return card

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
                  valid move!
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
        bad_moves = set()
        for move_type, draws, cards in stack_moves:
            if (
                draws == 0
                and (cards[0].num in solo_cards or cards[0].num == 13)
                and not moves_on_table
            ):
                # This stack move is a solo move, but we should only return it
                # IF there are no 0 draw moves already available
                return {(move_type, draws, cards)}

            # Check if the move would be a bad move.
            if self._bad_move(move_type, cards, card_counts):
                bad_moves.add((move_type, draws, cards))

        moves.update(stack_moves)

        return moves - bad_moves

    def _bad_move(
        self,
        move_type: MoveType,
        cards: tuple[Card, Card],
        card_counts: Counter[int],
    ) -> bool:
        """Check that if we play this move, would we put the baord in a bad state?

        Known bad moves include causing the game to end up with a pair that blocks each other.
        """
        if not self._optimise_blocked_by:
            return False
        if move_type != MoveType.StackMatch:
            raise NotImplementedError()

        if len(cards) == 1:
            # It's just a King - never a bad move!
            return False

        left_card, right_card = cards

        if card_counts[left_card.num] > 2:
            # Could be a bad move.. but not sure, let's just assume right now it isn't
            return False

        # Check if the remaining pair is on the table
        left_table_card = next(
            (card for card in self.cards if card.num == left_card.num), None
        )
        right_table_card = next(
            (card for card in self.cards if card.num == right_card.num), None
        )

        if left_table_card is None or right_table_card is None:
            # Shouldn't be a bad move?
            return False

        # Now check if one is blocked by the other?
        if left_table_card in self.blocked_by or right_table_card in self.blocked_by:
            # Pretty bad move!
            return True

        # Probably not a bad move?
        return False

    def play_move(self, move: Move) -> int:
        """Play a move and return the current number of moves the board is at"""
        move_type, draws, cards = move

        if draws:
            self.stack.draw(draws)
            self.moves += draws

        # TODO: No need to use types, given that we can just check if cards are on board or stack
        # NOTE: That might be slower though?
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

    def _remove_cards(self, cards_to_remove: Card | Sequence[Card]) -> None:
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

            # Also check if the card was blocking another
            freed_cards = set()
            for blocked_card, blocking_cards in self.blocked_by.items():
                if card_to_remove in blocking_cards:
                    blocking_cards.remove(card_to_remove)
                if not blocking_cards:
                    freed_cards.add(blocked_card)
            for freed_card in freed_cards:
                del self.blocked_by[freed_card]

            # Remove the card
            del self.cards[card_to_remove]

    @property
    def state(self) -> str:
        moves = str(self.moves)
        card_state = "".join(
            [f"{card.value}:{val.edge_state}" for card, val in self.cards.items()]
        )
        stack_state = "".join([card.value for card in self.stack.cards if card])
        stack_idx = str(self.stack.idx)
        return "|".join([moves, card_state, stack_idx, stack_state])

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
