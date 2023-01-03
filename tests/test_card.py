from spider_solver.board import Card


def test_card_init():
    stack_card = Card(13)

    assert str(stack_card) == "<Card K: In stack>"

    board_card = Card(1)

    assert str(board_card) == "<Card A: In stack>"


def test_card_match():
    king = Card(13)

    assert king.match == 13  # King will match itself

    ace = Card(1)

    assert ace.match == 12
