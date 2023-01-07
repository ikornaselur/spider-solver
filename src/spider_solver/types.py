from __future__ import annotations

from enum import Enum
from typing import TypeAlias

from spider_solver.card import Card


class MoveType(Enum):
    BoardMatch = "BoardMatch"
    BoardStackMatch = "BoardStackMatch"
    StackMatch = "StackMatch"


# The number of draws required from the stack
Draws: TypeAlias = int
Move: TypeAlias = tuple[MoveType, Draws, tuple[Card, ...]]
