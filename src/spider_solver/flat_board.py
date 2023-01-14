from __future__ import annotations

from collections.abc import Sequence

from spider_solver.card import Card
from spider_solver.exceptions import IllegalMove, SpiderException
from spider_solver.stack import Stack
from spider_solver.types import Move, MoveType

blockers_map = {
    0: set(),
    1: {0},
    2: {0},
    3: {1, 0},
    4: {1, 2, 0},
    5: {2, 0},
    6: {3, 1, 0},
    7: {3, 4, 1, 2, 0},
    8: {4, 5, 1, 2, 0},
    9: {5, 2, 0},
    10: {6, 3, 1, 0},
    11: {6, 7, 3, 4, 1, 2, 0},
    12: {7, 8, 3, 4, 5, 1, 2, 0},
    13: {8, 9, 4, 5, 1, 2, 0},
    14: {9, 5, 2, 0},
    15: {10, 6, 3, 1, 0},
    16: {10, 11, 6, 7, 3, 4, 1, 2, 0},
    17: {11, 12, 6, 7, 8, 3, 4, 5, 1, 2, 0},
    18: {12, 13, 7, 8, 9, 3, 4, 5, 1, 2, 0},
    19: {13, 14, 8, 9, 4, 5, 1, 2, 0},
    20: {14, 9, 5, 2, 0},
    21: {15, 10, 6, 3, 1, 0},
    22: {15, 16, 10, 11, 6, 7, 3, 4, 1, 2, 0},
    23: {16, 17, 10, 11, 12, 6, 7, 8, 3, 4, 5, 1, 2, 0},
    24: {17, 18, 11, 12, 13, 6, 7, 8, 9, 3, 4, 5, 1, 2, 0},
    25: {18, 19, 12, 13, 14, 7, 8, 9, 3, 4, 5, 1, 2, 0},
    26: {19, 20, 13, 14, 8, 9, 4, 5, 1, 2, 0},
    27: {20, 14, 9, 5, 2, 0},
}

blocks_cards_map = {
    0: (None, None),
    1: (0, None),
    2: (0, None),
    3: (1, None),
    4: (1, 2),
    5: (2, None),
    6: (3, None),
    7: (3, 4),
    8: (4, 5),
    9: (5, None),
    10: (6, None),
    11: (6, 7),
    12: (7, 8),
    13: (8, 9),
    14: (9, None),
    15: (10, None),
    16: (10, 11),
    17: (11, 12),
    18: (12, 13),
    19: (13, 14),
    20: (14, None),
    21: (15, None),
    22: (15, 16),
    23: (16, 17),
    24: (17, 18),
    25: (18, 19),
    26: (19, 20),
    27: (20, None),
}

# What cards are blocking X
blocked_by_map = {
    0: {
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        8,
        9,
        10,
        11,
        12,
        13,
        14,
        15,
        16,
        17,
        18,
        19,
        20,
        21,
        22,
        23,
        24,
        25,
        26,
        27,
    },
    1: {3, 4, 6, 7, 8, 10, 11, 12, 13, 15, 16, 17, 18, 19, 21, 22, 23, 24, 25, 26},
    2: {4, 5, 7, 8, 9, 11, 12, 13, 14, 16, 17, 18, 19, 20, 22, 23, 24, 25, 26, 27},
    3: {6, 7, 10, 11, 12, 15, 16, 17, 18, 21, 22, 23, 24, 25},
    4: {7, 8, 11, 12, 13, 16, 17, 18, 19, 22, 23, 24, 25, 26},
    5: {8, 9, 12, 13, 14, 17, 18, 19, 20, 23, 24, 25, 26, 27},
    6: {10, 11, 15, 16, 17, 21, 22, 23, 24},
    7: {11, 12, 16, 17, 18, 22, 23, 24, 25},
    8: {12, 13, 17, 18, 19, 23, 24, 25, 26},
    9: {13, 14, 18, 19, 20, 24, 25, 26, 27},
    10: {15, 16, 21, 22, 23},
    11: {16, 17, 22, 23, 24},
    12: {17, 18, 23, 24, 25},
    13: {18, 19, 24, 25, 26},
    14: {19, 20, 25, 26, 27},
    15: {21, 22},
    16: {22, 23},
    17: {23, 24},
    18: {24, 25},
    19: {25, 26},
    20: {26, 27},
    21: set(),
    22: set(),
    23: set(),
    24: set(),
    25: set(),
    26: set(),
    27: set(),
}

"""
This is really helpful, trust me:
      0
     1 2
    3 4 5
   6 7 8 9
  0 1 2 3 4
 5 6 7 8 9 0
1 2 3 4 5 6 7
"""


class FlatBoard:
    stack: Stack
    cards: list[Card]
    moves: int
    leaf_idxs: set[int]
    completed: bool
    _card_counts: dict[int, int]

    def __init__(
        self, rows: list[list[int]], stack: list[int], error_handle: bool = False
    ) -> None:
        self.cards = [
            Card(num, row=row_idx, col=col_idx)
            for row_idx, row in enumerate(rows)
            for col_idx, num in enumerate(row)
        ]
        self.stack = Stack.from_ints(stack)
        self.leaf_idxs = set(range(21, 28))
        self.moves = 0
        self.completed = False
        self._error_handle = error_handle

        # Set initial card counts
        self._card_counts = {key: 4 for key in range(1, 14)}

    @property
    def leaves(self) -> set[Card]:
        return set(self.cards[idx] for idx in self.leaf_idxs)

    def remove_cards(self, cards_to_remove: Card | Sequence[Card]) -> None:
        if isinstance(cards_to_remove, Card):
            cards_to_remove = [cards_to_remove]

        if self._error_handle:
            # Validate
            for card in cards_to_remove:
                # Make sure they are leaves
                if card not in self.leaves:
                    raise IllegalMove("Card is blocked by other cards")

        # Find the index of the cards to remove
        card_idxs = [self.cards.index(card) for card in cards_to_remove]

        # One by one, remove those indexes and check if we introduce a new leaf
        leaf_candidates = set()
        for card_idx in card_idxs:
            self.leaf_idxs.remove(card_idx)
            if card_idx == 0:
                self.completed = True

            # Get what it blocks and check if those are still blocked by
            # something else
            for blocked_card in blocks_cards_map[card_idx]:
                if blocked_card is not None:
                    leaf_candidates.add(blocked_card)

        # Remove candidates that are blocked by other candidates, as if those
        # blockers are going in they are going to block the previous card (this
        # hardly makes any sense, but it should be obvious.. right?)
        candidate_blockers = set()
        for candidate in leaf_candidates:
            candidate_blockers.update(blockers_map[candidate])

        # And now check the ones that aren't blocked by other candidates
        for candidate in leaf_candidates - candidate_blockers:
            if not blocked_by_map[candidate] & self.leaf_idxs:
                # This card has just become a leaf!
                self.leaf_idxs.add(candidate)

        # Also reduce the counts..
        for card in cards_to_remove:
            self._card_counts[card.num] -= 1

    def get_moves(self) -> set[Move]:
        # Check first for kings in the leaves
        for card in self.leaves:
            if card.num == 13:
                return {(MoveType.BoardMatch, 0, (card,))}

        # Otherwise let's build up some moves..
        moves = set()
        solo_cards = {key for key, val in self._card_counts.items() if val == 1}

        # Check for any matches on the table itself
        moves_on_table = False
        for leaf in self.leaves:
            for match in (
                pot_match for pot_match in self.leaves if pot_match.match == leaf.num
            ):
                if leaf.num > match.num:
                    leaf, match = match, leaf  # XXX: Is this necessary?
                if leaf.num in solo_cards:
                    # Last pair match, only logical move
                    return {(MoveType.BoardMatch, 0, (leaf, match))}
                else:
                    moves.add((MoveType.BoardMatch, 0, (leaf, match)))
                    moves_on_table = True

        # Check for stack matches
        # TODO: Refactor stack to simplify
        for leaf in self.leaves:
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
        # TODO: Refactor stack to simplify
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

    def play_move(self, move: Move) -> None:
        move_type, draws, cards = move
        if draws:
            self.stack.draw(draws)
            self.moves += draws

        match (move_type, cards):
            case (MoveType.BoardMatch, cards):
                self.remove_cards(cards)
            case (MoveType.BoardStackMatch, (board_card, stack_card)):
                if self._error_handle and (
                    not board_card.on_board ^ stack_card.on_board
                ):
                    raise SpiderException(
                        "Expected one card to be on board and other on stack"
                    )
                # XXX: Do I need to?
                if not board_card.on_board:
                    # Flip them around to be correct
                    board_card, stack_card = stack_card, board_card

                if (
                    self._error_handle
                    and stack_card is not self.stack.peek
                    and stack_card is not self.stack.prev
                ):
                    raise IllegalMove("Unable to match a stack card that isn't visible")

                self.stack.remove_cards(stack_card)
                self._card_counts[stack_card.num] -= 1
                self.remove_cards(board_card)
            case (MoveType.StackMatch, cards):
                self.stack.remove_cards(cards)
                self._card_counts[cards[0].num] -= 1
                if len(cards) == 2:
                    self._card_counts[cards[1].num] -= 1
            case _:
                raise IllegalMove("Unmatched move")

        self.moves += 1

    @property
    def state(self) -> str:
        moves = str(self.moves)
        card_state = ":".join(sorted(str(idx) for idx in self.leaf_idxs))
        stack_state = "".join([card.value for card in self.stack.cards if card])
        stack_idx = str(self.stack.idx)
        return "|".join([moves, card_state, stack_idx, stack_state])

    def __repr__(self) -> str:
        removed_cards = set()
        for leaf_idx in self.leaf_idxs:
            removed_cards.update(blocked_by_map[leaf_idx])

        rows = [
            [0],
            [1, 2],
            [3, 4, 5],
            [6, 7, 8, 9],
            [10, 11, 12, 13, 14],
            [15, 16, 17, 18, 19, 20],
            [21, 22, 23, 24, 25, 26, 27],
        ]

        out = ""
        for row in rows:
            for card_idx in row:
                if card_idx in removed_cards:
                    card = "_"
                else:
                    card = self.cards[card_idx].value
                out += f"{card} "
            out += "\n"

        return out

    def __str__(self) -> str:
        return f"<FlatBoard ({self.moves} moves)>"
