from spider_solver.board import Board, card_from_raw
from spider_solver.types import MoveType


def test_board_get_moves(board: Board):
    moves = list(board.get_moves())

    assert len(moves) == 23


def test_flat_board_card_removal():
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

    # Check that they flatten properly
    assert card_from_raw(board.cards[0]) == 8
    assert card_from_raw(board.cards[1]) == 7
    assert card_from_raw(board.cards[3]) == 12

    assert len(board.cards) == 1 + 2 + 3 + 4 + 5 + 6 + 7

    # Bottom corners
    assert card_from_raw(board.cards[21]) == 13
    assert card_from_raw(board.cards[27]) == 3

    # Leaves
    assert board.leaf_idxs == {21, 22, 23, 24, 25, 26, 27}
    assert len(board.leaves) == 7
    for i in [21, 22, 23, 24, 25, 26, 27]:
        assert board.cards[i] in board.leaves

    # Remove one of the leaves
    board.remove_cards([board.cards[21]])

    # Check that leaves are now one less
    assert len(board.leaves) == 6
    assert board.leaf_idxs == {22, 23, 24, 25, 26, 27}

    # Remove the next card at the bottom, which should keep leaves at 6,
    # because the one in the row above gets added instead
    board.remove_cards([board.cards[22]])
    assert len(board.leaves) == 6
    assert board.leaf_idxs == {15, 23, 24, 25, 26, 27}
    assert board.cards[15] in board.leaves


def test_flat_board_card_removal_edges_issue():
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

    board.remove_cards([board.cards[22], board.cards[26]])
    assert board.leaf_idxs == {21, 23, 24, 25, 27}

    board.remove_cards([board.cards[23], board.cards[27]])
    assert board.leaf_idxs == {16, 20, 21, 24, 25}

    board.remove_cards([board.cards[20], board.cards[24]])
    assert board.leaf_idxs == {16, 17, 21, 25}


def test_flat_board_moves():
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

    # Should just be one obvious move, remove the king
    moves = board.get_moves()
    assert len(moves) == 1
    move = moves.pop()
    assert len(move[2]) == 1
    card = move[2][0]
    assert card == board.cards[21]
    assert card in board.leaves

    # Let's play that move!
    board.play_move(move)

    assert board.moves == 1
    assert len(board.leaves) == 6
    assert card not in board.leaves

    # Let's get more moves
    moves = board.get_moves()
    assert len(moves) == 20

    # Let's try to remove cards from the stack next!
    # We should have the following move available..
    next_move = (MoveType.BoardStackMatch, 2, (14, 36))
    assert next_move in moves

    # Let's play it
    board.play_move(next_move)


def test_flat_board_get_stack_draws():
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
    board.stack_idx = 0

    draws = board._get_stack_draws(6)
    assert len(draws) == 2  # Only two sixes in the stack
    assert draws == [0, 3]

    # Let's ensure that if the card is visible on the left on the stack, we
    # don't need to draw to see it
    board.stack_idx = 1
    draws = board._get_stack_draws(6)
    assert len(draws) == 2
    assert draws == [-1, 2]

    # Then, if we have to go _around_ the stack, we need to make sure the count
    # accounts for the deck reset
    board.stack_idx = 2
    draws = board._get_stack_draws(6)
    assert len(draws) == 2
    assert draws == [1, 23]

    # Ensure that if card is visible both as left and right card, that is correctly reflected
    board.stack_idx = 6
    draws = board._get_stack_draws(13)
    assert len(draws) == 3
    assert draws == [-1, 0, 15]


def test_flat_board_stack_moves():
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
    board.stack_idx = 7

    """
    Matches that should be possible:
        * Draw 0 and match a K on the left (draw count will be -1)
        * Draw 6 and match 2 + J
        * Draw 12 and match 9 + 4
        * Draw 14 and match a K on the right
        * Draw 23 and match a K on the right
    """

    moves = board._get_stack_moves()

    assert len(moves) == 5

    # Order the moves by draws
    ordered = sorted(list(moves), key=lambda m: m[1])

    # Assert the draw count
    assert ordered[0][1] == -1
    assert ordered[1][1] == 6
    assert ordered[2][1] == 12
    assert ordered[3][1] == 14

    # Let's test these values
    for move in ordered:
        # Reset every time
        board.stack_idx = 7
        board._stack_draw(move[1])
        if card_from_raw(move[2][0]) == 13:
            # King is special..
            if move[1] == -1:
                # On the left
                assert (
                    board.stack[board.stack_idx - 1] == move[2][0]
                ), f"Failed for: {move}"
            else:
                # On the right
                assert board.stack[board.stack_idx] == move[2][0], f"Failed for: {move}"
        else:
            assert board.stack[board.stack_idx - 1] == move[2][0], f"Failed for: {move}"
            assert board.stack[board.stack_idx] == move[2][1], f"Failed for: {move}"


def test_flat_board_stack_draw_issue():
    # fmt: off
    board = Board(
        rows=[
                      [8],
                     [7, 5],  # noqa     It's just easier to visualise
                   [12, 1, 4],  # noqa   like this!
                  [11, 7, 1, 6],  # noqa 
                [12, 3, 1, 12, 7],  # noqa
              [6, 2, 10, 5, 13, 9],  # noqa
            [5, 2, 10, 4, 2, 11, 3],  # noqa
        ],
        stack=[6, 8, 11, 6, 8, 13, 13, 8, 10, 12, 3, 4,
               2, 11, 1, 7, 10, 9, 9, 4, 3, 13, 9, 5]
    )
    board.leaf_idxs = {13, 15, 16, 17}
    board.stack_idx = 1
    board.stack = [
        44, 25, 38, 46, 35, 50, 28, 29, 40, 49, 39, 45, 48, 21, 34, 42, 41, 51, 47, 43,
    ]
    # fmt: on

    # We have a king visible
    assert card_from_raw(board.stack[board.stack_idx]) == 13

    # We should have a move to remove that king without any draws
    moves = board.get_moves()

    expected_move = (MoveType.StackMatch, 0, (board.stack[board.stack_idx],))
    assert expected_move in moves


def test_flat_board_match_left_card_on_stack_issue():
    # fmt: off
    board = Board(
        rows=[
                      [8],
                     [7, 5],  # noqa     It's just easier to visualise
                   [12, 1, 4],  # noqa   like this!
                  [11, 7, 1, 6],  # noqa 
                [12, 3, 1, 12, 7],  # noqa
              [6, 2, 10, 5, 13, 9],  # noqa
            [5, 2, 10, 4, 2, 11, 3],  # noqa
        ],
        stack=[6, 8, 11, 6, 8, 13, 13, 8, 10, 12, 3, 4,
               2, 11, 1, 7, 10, 9, 9, 4, 3, 13, 9, 5]
    )

    board.leaf_idxs = {12, 13, 15, 16}
    board.stack_idx = 4
    board.stack = [44, 46, 35, 50, 29, 40, 49, 39, 45, 48, 21, 34, 42, 41, 51, 47, 43]
    board.moves = 15
    # fmt: on

    # Should be able to play the following move
    expected_move = (MoveType.BoardStackMatch, 0, (26, 50))

    moves = board.get_moves()

    assert expected_move in moves

    # Play the move
    board.play_move(expected_move)

    # Stack should now show 10 on the left and 4 on the right
    assert card_from_raw(board.stack[board.stack_idx - 1]) == 10
    assert card_from_raw(board.stack[board.stack_idx]) == 4
