import json
import sys
from pathlib import Path
from typing import TypedDict

from rich.console import Console

from spider_solver.flat_board import FlatBoard as Board
# from spider_solver.board import Board
from spider_solver.game import describe_solution, simulate

console = Console()

card_map = {
    "a": 1,
    "0": 10,
    "j": 11,
    "d": 12,
    "k": 13,
}

LEVELS_FILE = Path("levels.json")
LEVEL = 1


class GameInput(TypedDict):
    board: str
    stack: str
    known_min_moves: int


def get_games() -> list[GameInput]:
    if LEVELS_FILE.exists():
        with LEVELS_FILE.open() as f:
            return json.load(f)
    else:
        console.print("[red]games.json not found. Just using example game.")
        return [
            {
                "board": "5 30 j2d k689 d8357 564390 6daakk7",
                "stack": "49d083562920k87j4jaa47j2",
                "known_min_moves": 33,
            }
        ]


def parse_row(raw_rows: str) -> list[list[int]]:
    rows: list[str] = raw_rows.strip().split(" ")
    return [[card_map.get(char) or int(char) for char in row.strip()] for row in rows]


def parse_stack(raw_stack: str) -> list[int]:
    return [card_map.get(char) or int(char) for char in raw_stack]


def main():
    games = get_games()

    if LEVEL < 1 or LEVEL > len(games):
        console.print("[red]Level not defined.")
        sys.exit(1)

    game = games[LEVEL - 1]
    rows = parse_row(game["board"])
    stack = parse_stack(game["stack"])

    initial_board = Board(rows=rows, stack=stack)

    console.print("Solving game:")
    console.print(repr(initial_board))

    # Allow top 3 moves for first 5 actions
    first_top_moves = 3
    first_games = 5
    # Then fallback to 2
    top_moves = 2

    (solution, _) = simulate(
        initial_board,
        known_min_moves=game["known_min_moves"],
        top_moves=top_moves,
        first_top_moves=first_top_moves,
        first_games=first_games,
    )

    """
    with open("solution_trie.json", "w") as f:
        json.dump(solution_trie, f, indent=2)

    """

    describe_solution(initial_board, solution)


if __name__ == "__main__":
    main()
