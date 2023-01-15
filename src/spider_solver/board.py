from __future__ import annotations

from collections.abc import Sequence

from spider_solver.exceptions import IllegalMove
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

# Num + row + col
# Card = tuple[int, int, int]


def card_from_raw(val: int) -> int:
    """A raw value will be from 0 to 51

    Aces will be 0, 13, 26 and 39 for example

    Turns 0, 13, 26 and 39 to be "1" for Ace
    """
    return (val % 13) + 1


def card_pos(cards: list[int], card: int) -> str:
    idx = cards.index(card)
    # I'm so damn lazy
    if idx == 0:
        return "On board 1st row, 1st card"
    if idx in [1, 2]:
        return f"On board 2nd row, card {idx}"
    if idx in [3, 4, 5]:
        return f"On board 3rd row, card {idx - 2}"
    if idx in [6, 7, 8, 9]:
        return f"On board 4th row, card {idx - 5}"
    if idx in [10, 11, 12, 13, 14]:
        return f"On board 5th row, card {idx - 9}"
    if idx in [15, 16, 17, 18, 19, 20]:
        return f"On board 6th row, card {idx - 14}"
    if idx in [21, 22, 23, 24, 25, 26, 27]:
        return f"On board 7th row, card {idx - 20}"
    return "No idea"


def pretty_card(val: int) -> str:
    match card_from_raw(val):
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
        case other:
            return str(other)


def match(val: int) -> int:
    """Get the card value that would match with this card

    1 will return 12 (Ace matchs with Jack)
    13 will return 13 (King matches with itself)
    """
    return (13 - val) or 13


def cards_match(a: int, b: int) -> bool:
    """Check if two cards are a matchin pair"""
    a = card_from_raw(a)
    b = card_from_raw(b)
    return match(a) == b


class Board:
    stack: list[int]
    stack_idx: int
    cards: list[int]
    moves: int
    leaf_idxs: set[int]
    completed: bool
    _card_counts: dict[int, int]

    def __init__(self, rows: list[list[int]], stack: list[int]) -> None:
        self.cards = []
        self._card_counts = {key: 0 for key in range(1, 14)}
        self._stack_counts = {key: 0 for key in range(1, 14)}

        # Set the board cards
        for card in [num for row in rows for num in row]:
            # Store the cards offset based on the counts
            # First A will be 0, next A will be 13, then 26 and 39
            count = self._card_counts[card]
            self.cards.append((card - 1) + 13 * count)
            self._card_counts[card] += 1

        # Set the board cards
        self.stack = []
        self.stack_idx = 0
        for card in stack:
            count = self._card_counts[card]
            self.stack.append((card - 1) + 13 * count)
            self._card_counts[card] += 1
            self._stack_counts[card] += 1

        self.leaf_idxs = set(range(21, 28))
        self.moves = 0
        self.completed = False

    @property
    def leaves(self) -> set[int]:
        return set(self.cards[idx] for idx in self.leaf_idxs)

    def remove_cards(self, cards_to_remove: Sequence[int]) -> None:
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
            self._card_counts[card_from_raw(card)] -= 1

    def remove_stack_cards(self, cards_to_remove: Sequence[int]) -> None:
        # I should error check here, but again, not wasting any cycles on it! NEW WAY IS FAST AND DANGEROUS
        # Later addition to this comment: There was was an issue here in the end..
        for card in cards_to_remove:
            if self.stack_idx > 0 and self.stack[self.stack_idx - 1] == card:
                # Need to shift back since the right card will have moved up
                self.stack_idx -= 1
            self.stack.remove(card)

    def _get_stack_draws(self, val: int) -> list[int]:
        """Return a list of how many draws are needed to find the card by value"""
        draws: list[int] = []

        stack_len = len(self.stack)

        if self.stack_idx > 0:
            # We have to account for a left card being visible
            if card_from_raw(self.stack[self.stack_idx - 1]) == val:
                draws.append(-1)  # "Draw -1" means it's the previous visible card
        for idx, card in enumerate(self.stack[self.stack_idx :]):
            if card_from_raw(card) == val:
                draws.append(idx)
        for idx, card in enumerate(self.stack[: max(self.stack_idx - 1, 0)]):
            if card_from_raw(card) == val:
                draws.append(idx + stack_len - self.stack_idx + 1)

        return draws

    def _get_stack_moves(self) -> set[Move]:
        moves = set()

        if self.stack_idx > 0:
            # Check if the two visible cards match
            left = self.stack[self.stack_idx - 1]
            if self.stack_idx < len(self.stack):
                if cards_match(left, (right := self.stack[self.stack_idx])):
                    moves.add(
                        (
                            MoveType.StackMatch,
                            0,
                            (left, right),
                        )
                    )
            # Also check if there is a king visible on the left side
            if card_from_raw(left) == 13:
                moves.add((MoveType.StackMatch, -1, (left,)))

        # Lets check the right side solo as well for king
        if self.stack_idx < len(self.stack):
            if card_from_raw((right := self.stack[self.stack_idx])) == 13:
                moves.add((MoveType.StackMatch, 0, (right,)))

        # Check if any pairs match going further up the stack
        upper_stack = self.stack[self.stack_idx :]
        for draw, (left, right) in enumerate(zip(upper_stack, upper_stack[1:])):
            if card_from_raw(right) == 13:
                # Get rid of that king!
                moves.add((MoveType.StackMatch, draw + 1, (right,)))
            elif cards_match(left, right):
                moves.add((MoveType.StackMatch, draw + 1, (left, right)))

        # Check if any pairs after resetting the stack
        lower_stack = self.stack[: self.stack_idx]
        stack_len = len(self.stack)
        for draw, (left, right) in enumerate(zip(lower_stack, lower_stack[1:])):
            if cards_match(left, right):
                moves.add(
                    (
                        MoveType.StackMatch,
                        draw + stack_len - self.stack_idx + 1,
                        (left, right),
                    )
                )

        return moves

    def get_moves(self) -> set[Move]:
        # Check first for kings in the leaves
        for card in self.leaves:
            if card_from_raw(card) == 13:
                return {(MoveType.BoardMatch, 0, (card,))}

        # Otherwise let's build up some moves..
        moves = set()
        solo_cards = {key for key, val in self._card_counts.items() if val == 1}

        # Check for any matches on the table itself
        moves_on_table = False
        already_matched = set()
        for leaf in self.leaves:
            for leaf_match in (
                pot_match for pot_match in self.leaves if cards_match(leaf, pot_match)
            ):
                if leaf_match in already_matched:
                    continue
                already_matched.update({leaf, leaf_match})
                if card_from_raw(leaf) in solo_cards:
                    # Last pair match, only logical move
                    return {(MoveType.BoardMatch, 0, (leaf, leaf_match))}
                else:
                    moves.add((MoveType.BoardMatch, 0, (leaf, leaf_match)))
                    moves_on_table = True

        # Check for stack matches
        for leaf in self.leaves:
            leaf_val = card_from_raw(leaf)
            leaf_match = match(leaf_val)
            if not self._stack_counts[leaf_match]:
                # Match not in the stack
                continue

            # We have some potential matches to make in from the stack.. let's find them
            draws = self._get_stack_draws(leaf_match)
            for draw in draws:
                stack_card_idx = self.stack_idx + draw
                if stack_card_idx > (stack_len := len(self.stack)):
                    # Need to wrap the stack!
                    stack_card_idx -= stack_len + 1  # One for flippage
                stack_card = self.stack[stack_card_idx]
                if leaf_val in solo_cards and draw <= 0:
                    # We should get rid of it ASAP
                    return {
                        (MoveType.BoardStackMatch, max(draw, 0), (leaf, stack_card))
                    }
                # Left side of visible stack card is -1, no need to draw, hence max()
                moves.add(
                    (
                        MoveType.BoardStackMatch,
                        max(draw, 0),
                        (leaf, stack_card),
                    )
                )

        # Check for any moves that match in the stack
        stack_moves = self._get_stack_moves()
        if not moves_on_table:
            for move_type, draws, cards in stack_moves:
                if draws != 0:
                    continue
                if (
                    card_val := card_from_raw(cards[0])
                ) == 13 or card_val in solo_cards:
                    # This stack move is a solo move, but we should only return it
                    # IF there are no 0 draw moves already available
                    return {(move_type, draws, cards)}

        moves.update(stack_moves)

        return moves

    def _stack_draw(self, draws: int) -> None:
        if draws <= 0:
            return
        self.stack_idx += draws
        if self.stack_idx == len(self.stack):
            raise NotImplementedError(
                "Do I need to handle the case of last card but no flip?"
            )

        if self.stack_idx > len(self.stack):
            self.stack_idx -= len(self.stack) + 1  # Extra one for the stack reset

        self.moves += draws

    def play_move(self, move: Move) -> None:
        move_type, draws, cards = move
        self._stack_draw(draws)

        match (move_type, cards):
            case (MoveType.BoardMatch, cards):
                self.remove_cards(cards)
            case (MoveType.BoardStackMatch, (board_card, stack_card)):
                # Will raise ValueError if flipped.. Not wasting cycles on
                # error checking, they shouldn't be mixed up in the first
                # place!

                self.remove_stack_cards([stack_card])
                self._card_counts[card_from_raw(stack_card)] -= 1
                self.remove_cards([board_card])
            case (MoveType.StackMatch, cards):
                self.remove_stack_cards(cards)
                self._card_counts[card_from_raw(cards[0])] -= 1
                if len(cards) == 2:
                    self._card_counts[card_from_raw(cards[1])] -= 1
            case _:
                raise IllegalMove("Unmatched move")

        self.moves += 1

    @property
    def state(self) -> str:
        moves = str(self.moves)
        card_state = ":".join(sorted(str(idx) for idx in self.leaf_idxs))
        stack_state = ":".join(str(card) for card in self.stack)
        stack_idx = str(self.stack_idx)
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
                    card = card_from_raw(self.cards[card_idx])
                out += f"{card} "
            out += "\n"

        return out

    def __str__(self) -> str:
        return f"<Board ({self.moves} moves)>"
