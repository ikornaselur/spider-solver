from spider_solver.board import Board, Edges, MoveType
from spider_solver.card import Card


def test_board_init(unique_board: Board):
    board = unique_board
    # Just checking basic stuff
    assert len(board.cards) == 28
    assert len(board.stack.cards) == 5  # Including the empty space at the back

    # There should be no cards pointing at the top card
    for edges in board.cards.values():
        assert edges.left != 1 and edges.right != 1

    # Bottom level cards shouldn't point at any cards
    for num in [22, 23, 24, 25, 26, 27, 28]:
        card = next(c for c in board.cards if c.num == num)
        assert len(board.cards[card]) == 0


def test_board_leaves(unique_board: Board):
    board = unique_board
    assert len(board.leaves) == 7

    assert any(leaf.num == 22 for leaf in board.leaves)
    assert any(leaf.num == 23 for leaf in board.leaves)
    assert any(leaf.num == 24 for leaf in board.leaves)
    assert any(leaf.num == 25 for leaf in board.leaves)
    assert any(leaf.num == 26 for leaf in board.leaves)
    assert any(leaf.num == 27 for leaf in board.leaves)
    assert any(leaf.num == 28 for leaf in board.leaves)


def test_board_get_moves(board: Board):
    moves = list(board.get_moves())

    assert len(moves) == 23


def test_board_get_moves_with_king():
    # fmt: off
    board = Board(
        rows=[
                      [8],
                     [7, 5],  # noqa     It's just easier to visualise
                   [12, 1, 4],  # noqa   like this!
                  [11, 7, 1, 6],  # noqa 
                [12, 3, 1, 12, 7],  # noqa
              [6, 2, 10, 5, 5, 9],  # noqa
            [13, 2, 10, 4, 2, 11, 3],  # noqa
        ],
        stack=[6, 8, 11, 6, 8, 13, 13, 8, 10, 12, 3, 4,
               2, 11, 1, 7, 10, 9, 9, 4, 3, 13, 9, 5],
    )
    # fmt: on
    moves = list(board.get_moves())

    assert len(moves) == 1
    move_type, draws, cards = moves.pop()
    assert move_type == MoveType.BoardMatch
    assert draws == 0
    assert len(cards) == 1
    assert cards[0].num == 13


def test_board_get_moves_with_solo_cards_on_table():
    # fmt: off
    board = Board(
        rows=[
                      [8],
                     [8, 5],  # noqa     It's just easier to visualise
                   [12, 1, 5],  # noqa   like this!
        ],
        stack=[8, 5],
        _validate=False,
    )
    # fmt: on
    moves = list(board.get_moves())

    assert len(moves) == 1
    move_type, draws, cards = moves.pop()
    assert move_type == MoveType.BoardMatch
    assert draws == 0
    assert len(cards) == 2
    assert cards[0].num == 1
    assert cards[1].num == 12


def test_board_get_moves_with_solo_card_on_table_and_stack():
    # fmt: off
    board = Board(
        rows=[
                      [8],
                     [8, 5],  # noqa     It's just easier to visualise
                   [5, 1, 5],  # noqa   like this!
        ],
        stack=[12, 8],
        _validate=False,
    )
    # fmt: on
    moves = list(board.get_moves())

    assert len(moves) == 1
    move_type, draws, cards = moves.pop()
    assert move_type == MoveType.BoardStackMatch
    assert draws == 0
    assert len(cards) == 2
    assert cards[0].num == 1
    assert cards[1].num == 12


def test_board_play_move(board: Board):
    assert repr(board) == "\n".join(
        [
            "       8    6",
            "      7 5",
            "     D A 4",
            "    J 7 A 6",
            "   D 3 A D 7",
            "  6 2 0 5 K 9",
            " 5 2 0 4 2 J 3",
        ]
    )

    # Find the move to match the right 2 + J
    right_two = next(card for card in board.cards if card.row == 6 and card.col == 4)
    jack = next(card for card in board.cards if card.row == 6 and card.col == 5)

    board.play_move((MoveType.BoardMatch, 0, (right_two, jack)))

    assert repr(board) == "\n".join(
        [
            "       8    6",
            "      7 5",
            "     D A 4",
            "    J 7 A 6",
            "   D 3 A D 7",
            "  6 2 0 5 K 9",
            " 5 2 0 4     3",
        ]
    )

    # Find the king and remove it
    king = next(card for card in board.cards if card.row == 5 and card.col == 4)
    board.play_move((MoveType.BoardMatch, 0, (king,)))

    assert repr(board) == "\n".join(
        [
            "       8    6",
            "      7 5",
            "     D A 4",
            "    J 7 A 6",
            "   D 3 A D 7",
            "  6 2 0 5   9",
            " 5 2 0 4     3",
        ]
    )

    # Remove the 10 and 3 next
    ten = next(card for card in board.cards if card.row == 6 and card.col == 2)
    three = next(card for card in board.cards if card.row == 6 and card.col == 6)

    # Also check that the three in row 5 gets unblocked by the ten we remove
    blocked_three = next(
        card for card in board.cards if card.row == 4 and card.col == 1
    )
    assert len(board.blocked_by[blocked_three]) == 2
    assert ten in board.blocked_by[blocked_three]

    board.play_move((MoveType.BoardMatch, 0, (ten, three)))

    assert ten not in board.blocked_by[blocked_three]

    assert repr(board) == "\n".join(
        [
            "       8    6",
            "      7 5",
            "     D A 4",
            "    J 7 A 6",
            "   D 3 A D 7",
            "  6 2 0 5   9",
            " 5 2   4",
        ]
    )

    # And then the 4 and 9
    four = next(card for card in board.cards if card.row == 6 and card.col == 3)
    nine = next(card for card in board.cards if card.row == 5 and card.col == 5)

    board.play_move((MoveType.BoardMatch, 0, (four, nine)))

    assert repr(board) == "\n".join(
        [
            "       8    6",
            "      7 5",
            "     D A 4",
            "    J 7 A 6",
            "   D 3 A D 7",
            "  6 2 0 5",
            " 5 2",
        ]
    )

    # And now we start matching from the stack, 7 on the board with 6 from the stack
    seven = next(card for card in board.cards if card.row == 4 and card.col == 4)
    six = board.stack.peek
    assert six is not None

    # Also check that the 6 in row 4 gets completely unblocked
    blocked_six = next(card for card in board.cards if card.row == 3 and card.col == 3)
    assert seven in board.blocked_by[blocked_six]

    board.play_move((MoveType.BoardStackMatch, 0, (seven, six)))

    # No longer blocked by anything!
    assert blocked_six not in board.blocked_by

    assert repr(board) == "\n".join(
        [
            "       8    8",
            "      7 5",
            "     D A 4",
            "    J 7 A 6",
            "   D 3 A D",
            "  6 2 0 5",
            " 5 2",
        ]
    )


def test_board_init_sets_up_blocked_by(board: Board) -> None:
    """
          8
         7 5
        D A 4
       J 7 A 6
      D 3 A D 7
     6 2 0 5 K 9
    5 2 0 4 2 J 3
    """
    assert len(board.blocked_by) == 9

    def check_at(row: int, col: int, num: int, count: int) -> None:
        card = board.get_card_at_row_col(row, col)
        assert card
        assert card.num == num
        assert len(blocks := board.blocked_by[card]) == count
        assert all(block_card.num == card.match for block_card in blocks)

    # The root card, 8, should be blocked by all three 5 cards
    check_at(0, 0, 8, 3)

    # 7 in 2nd row is blocked by a 6 in the 6th row
    check_at(1, 0, 7, 1)

    # D in 3rd row is blocked by an A in 5th row
    check_at(2, 0, 12, 1)

    # A in 3rd row is blocked by a D in 5th row
    check_at(2, 1, 1, 1)

    # J in 4th row
    check_at(3, 0, 11, 2)

    # A in 4th row
    check_at(3, 2, 1, 1)

    # 6 in 4th row
    check_at(3, 3, 6, 1)

    # 3 in 5th row
    check_at(4, 1, 3, 2)


def test_get_moves_doesnt_provide_obvious_bad_moves_deadlock():
    """Run analyse on level 1

    Move at 20 moves is to match 3 + 10, both on the stack. This puts the game
    in a bad state, because there is a 3 blocked by 10 on the game board and
    there are no 3 left to match with that 10 on the board.

    This move should not be offered at 20 moves! Figure out how to set up that
    state easily in a test and then assert the move isn't given..
    """

    # Initialise a board state that is known to have a deadlock move available
    board = Board(
        rows=[], stack=[6, 6, 8, 8, 12, 4, 10, 3, 1, 13, 9, 5], _validate=False
    )
    board.stack.idx = 7

    board.cards = {}

    A = 1
    J = 11
    D = 12
    K = 13
    _ = None

    # fmt: off
    rows = [
              [8],
             [7, 6],  # noqa
            [D, A, 4],  # noqa
           [J, 7, A, 6],  # noqa
          [D, 3, A, D, 7],  # noqa
         [_, _, 0, 5, K, 9],  # noqa
        [_, _, _, _, 2, _, _],  # noqa
    ]
    # fmt: on

    for row in range(6, -1, -1):
        for col, card in enumerate(rows[row]):
            if card is None:
                continue
            if card == 0:
                card = 10

            card = Card(card, row, col)
            rows[row][col] = card

            if row == 6:  # Bottom row
                board.cards[card] = Edges(None, None)
            else:  # Any other row
                board.cards[card] = Edges(rows[row + 1][col], rows[row + 1][col + 1])

            if row == 0 and col == 0:
                board.root_card = card

    # Populate the blocks
    board._walk(board.root_card)

    moves = board.get_moves()

    # At this point, if we match 0 and 3 that are visible in the stack, we can
    # not finish the game. This move will leave only a single pair of 10 + 3 in
    # the game and they are both on the table. The 10 is blocked by 3 at this
    # point, so game is impossible.

    # Ensure we have no 0 draw StackMatch moves, which would be to match the 10
    # and 3 on the stack
    bad_moves = [m for m in moves if m[1] == 0 and m[0] == MoveType.StackMatch]

    assert not bad_moves
