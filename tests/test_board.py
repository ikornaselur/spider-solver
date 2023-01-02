from spider_solver.board import Board


def test_board_init(unique_board: Board):
    board = unique_board
    # Just checking basic stuff
    assert len(board.cards) == 28
    assert len(board.stack.cards) == 4

    # There should be no cards pointing at the top card
    for edges in board.cards.values():
        assert not any(edge.num == 1 for edge in edges)

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

    assert len(moves) == 3
