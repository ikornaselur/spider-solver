from rich.console import Console
from rich.prompt import Prompt

from spider_solver.board import Move
from spider_solver.flat_board import FlatBoard as Board
from spider_solver.game import get_loc

console = Console()

card_map = {
    "a": 1,
    "0": 10,
    "j": 11,
    "d": 12,
    "k": 13,
}

example_game_raw = (
    "5 30 j2d k689 d8357 564390 6daakk7",
    "49d083562920k87j4jaa47j2",
    42,
)


def parse_row(raw_rows: str) -> list[list[int]]:
    rows: list[str] = raw_rows.strip().split(" ")
    return [[card_map.get(char) or int(char) for char in row.strip()] for row in rows]


def parse_stack(raw_stack: str) -> list[int]:
    return [card_map.get(char) or int(char) for char in raw_stack]


raw_rows, raw_stack, known_min_moves = example_game_raw
rows = parse_row(raw_rows)
stack = parse_stack(raw_stack)

board = Board(rows=rows, stack=stack)


def pretty_print(idx: int, move: Move) -> None:
    _, draws, cards = move
    if draws > 0:
        draw_str = f"Draw {draws} card{'s' if draws > 1 else ''} and "
    else:
        draw_str = ""

    if len(cards) == 1:
        cards_str = f"{'r' if draw_str else 'R'}emove [green]{cards[0].value}[/green] {get_loc(board, cards[0])}"
    else:
        cards_str = (
            f"{'m' if draw_str else 'M'}atch [green]{cards[1].value}[/green] {get_loc(board, cards[1])} and "
            f"[green]{cards[0].value}[/green] {get_loc(board, cards[0])}"
        )

    console.print(f"[{idx+1}] {draw_str}{cards_str}")


def main():
    moves_played = []
    while board.cards:
        console.rule("Current board state")
        console.print(repr(board))
        moves = sorted(board.get_moves(), key=lambda m: (m[1], str(m[2])))
        if not moves:
            console.print("[red]No moves available!")
            return
        option_count = min(len(moves), 5)
        console.rule(f"Top {option_count} moves")
        for idx, move in enumerate(moves[:5]):
            pretty_print(idx, move)
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
