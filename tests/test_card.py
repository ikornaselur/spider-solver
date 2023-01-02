from spider_solver.board import Card


def test_card_init():
    stack_card = Card(13)

    assert str(stack_card) == "<Card K: In stack>"

    board_card = Card(1, row=2, col=3)

    assert str(board_card) == "<Card A: On board 3rd row, 4th card>"


def test_card_match():
    king = Card(13)

    assert king.match == 13  # King will match itself

    ace = Card(1)

    assert ace.match == 12
