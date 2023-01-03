from typing import Iterable

import pytest

from spider_solver.board import Board


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
        _validate=False,
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
            [5, 2, 10, 4, 2, 11, 3],  # noqa
        ],
        stack=[6, 8, 11, 6, 8, 13, 13, 8, 10, 12, 3, 4,
               2, 11, 1, 7, 10, 9, 9, 4, 3, 13, 9, 5],
    )
    # fmt: on
