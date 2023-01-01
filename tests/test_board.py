from typing import Iterable

import pytest

from spider_solver.board import Board, Card, Stack


@pytest.fixture
def unique_board() -> Iterable[Board]:
    """A board with unique numbers on the cards for easier validation"""
    # fmt: off
    yield Board(
        rows=[
                      [1],
                     [2, 3],  # noqa     It's just easier to visualise
                    [4, 5, 6],  # noqa   like this!
                   [7, 8, 9, 10],  # noqa 
                [11, 12, 13, 14, 15],  # noqa
              [16, 17, 18, 19, 20, 21],  # noqa
            [22, 23, 24, 25, 26, 27, 28],  # noqa
        ],
        stack=[29, 30, 31, 32],
    )
    # fmt: on


@pytest.fixture
def board() -> Iterable[Board]:
    """A board with unique numbers on the cards for easier validation"""
    # fmt: off
    yield Board(
        rows=[
                      [8],
                     [7, 5],  # noqa     It's just easier to visualise
                   [12, 1, 4],  # noqa   like this!
                  [11, 7, 1, 6],  # noqa 
                [12, 3, 1, 12, 7],  # noqa
              [6, 2, 10, 5, 13, 9],  # noqa
            [5, 2, 10, 4, 2, 12, 3],  # noqa
        ],
        stack=[6, 8, 11, 6, 8, 13, 13, 8, 10, 12, 3, 4,
               2, 11, 1, 7, 10, 9, 9, 4, 3, 13, 9, 5],
    )
    # fmt: on


def test_card_init():
    card = Card(13)

    assert str(card) == "<Card K>"


def test_stack_init():
    cards = [Card(i) for i in range(1, 5)]
    stack = Stack(cards)

    assert str(stack) == "<Stack 1 2 3 4>"


def test_stack_draw():
    cards = [Card(i) for i in range(1, 5)]
    stack = Stack(cards)

    card = stack.peek()
    assert card.num == 1

    assert str(stack) == "<Stack 1 2 3 4>"

    card = stack.draw()
    assert card.num == 2

    assert str(stack) == "<Stack 2 3 4 1>"


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


def test_board_leafs(unique_board: Board):
    board = unique_board
    assert len(board.leafs) == 7

    assert any(leaf.num == 22 for leaf in board.leafs)
    assert any(leaf.num == 23 for leaf in board.leafs)
    assert any(leaf.num == 24 for leaf in board.leafs)
    assert any(leaf.num == 25 for leaf in board.leafs)
    assert any(leaf.num == 26 for leaf in board.leafs)
    assert any(leaf.num == 27 for leaf in board.leafs)
    assert any(leaf.num == 28 for leaf in board.leafs)
