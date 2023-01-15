import json
from pathlib import Path
from typing import TypedDict

from rich.console import Console
from rich.prompt import Prompt

from spider_solver.board import Board, Move, pretty_card
from spider_solver.game import get_loc

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


def pretty_print(board: Board, idx: int, move: Move) -> None:
    _, draws, cards = move
    if draws > 0:
        draw_str = f"Draw {draws} card{'s' if draws > 1 else ''} and "
    else:
        draw_str = ""

    if len(cards) == 1:
        cards_str = f"{'r' if draw_str else 'R'}emove [green]{pretty_card(cards[0])}[/green] {get_loc(board, cards[0])}"
    else:
        cards_str = (
            f"{'m' if draw_str else 'M'}atch [green]{pretty_card(cards[1])}[/green] {get_loc(board, cards[1])} and "
            f"[green]{pretty_card(cards[0])}[/green] {get_loc(board, cards[0])}"
        )

    console.print(f"[{idx+1}] {draw_str}{cards_str}")


def main():
    games = get_games()

    game = games[LEVEL - 1]

    rows = parse_row(game["board"])
    stack = parse_stack(game["stack"])

    board = Board(rows=rows, stack=stack)

    moves_played = []
    while board.cards:
        console.rule("Current board state")
        console.print(repr(board))
        console.print(f"{board.leaf_idxs=}")
        console.print(f"{board.stack_idx=}")
        console.print(f"{board.stack=}")
        console.print(f"{board.moves=}")
        if board.stack_idx > 0:
            console.print(
                f"Stack: {pretty_card(board.stack[board.stack_idx - 1])} {pretty_card(board.stack[board.stack_idx])}"
            )
        else:
            console.print(f"Stack: _ {pretty_card(board.stack[board.stack_idx])}")
        moves = sorted(board.get_moves(), key=lambda m: (m[1], str(m[2])))
        if not moves:
            console.print("[red]No moves available!")
            return
        option_count = min(len(moves), 5)
        console.rule(f"Top {option_count} moves")
        for idx, move in enumerate(moves[:5]):
            pretty_print(board, idx, move)
        option_raw = Prompt.ask("Play option", default="1")
        if (
            not option_raw.isdigit()
            or (option := int(option_raw)) < 1
            or option > option_count
        ):
            console.print("[red]Invalid option")
            continue

        moves_played.append(option)
        board.play_move(moves[option - 1])

    if not board.cards:
        console.print(f"[green]Game solved in {board.moves} moves!")
        console.print(f"Moves played: {moves_played}")
    else:
        console.print("[red]Uhm.. error?")


if __name__ == "__main__":
    main()
