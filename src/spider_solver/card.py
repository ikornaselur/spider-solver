from __future__ import annotations


class Card:
    num: int  # The value of the card from 1 to 13

    # Position metadata to identify duplicates. If not set, it could be in a
    # stack instead of the main board
    row: int | None
    col: int | None

    def __init__(
        self, num: int, row: int | None = None, col: int | None = None
    ) -> None:
        self.num = num
        self.row = row
        self.col = col

    @property
    def value(self) -> str:
        match self.num:
            case 1:
                return "A"
            case 10:
                return "0"  # Single width values for all cards
            case 11:
                return "J"
            case 12:
                return "D"
            case 13:
                return "K"
            case _:
                return str(self.num)

    @property
    def match(self) -> int:
        """The value that needs to match with this card

        The king will return the value 0, which means it can match by itself
        """
        return (13 - self.num) or 13

    @property
    def on_board(self) -> bool:
        """Whether the card is on the playing board or not

        If False, the card is in the stack
        """
        return self.row is not None and self.col is not None

    @property
    def pos(self) -> str:
        if self.row is None or self.col is None:
            return "In stack"

        match self.row:
            case 0:
                row = "1st"
            case 1:
                row = "2nd"
            case 2:
                row = "3rd"
            case _:
                row = f"{self.row + 1}th"
        match self.col:
            case 0:
                col = "1st"
            case 1:
                col = "2nd"
            case 2:
                col = "3rd"
            case _:
                col = f"{self.col + 1}th"

        return f"On board {row} row, {col} card"

    def __repr__(self) -> str:
        return f"<Card {self.value}: {self.pos}>"
