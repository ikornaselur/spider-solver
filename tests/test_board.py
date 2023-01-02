from spider_solver.board import Board, MoveType


def test_board_init(unique_board: Board):
    board = unique_board
    # Just checking basic stuff
    assert len(board.cards) == 28
    assert len(board.stack.cards) == 4

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
    board.play_move((MoveType.BoardMatch, 0, (king, )))

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
