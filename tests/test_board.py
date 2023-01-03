from spider_solver.board import Board, MoveType


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

    board.play_move((MoveType.BoardMatch, 0, (ten, three)))

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

    board.play_move((MoveType.BoardStackMatch, 0, (seven, six)))

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
