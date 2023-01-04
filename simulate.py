from rich.console import Console

from spider_solver.board import Board
from spider_solver.game import describe_solution, simulate

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
    33,
)



def parse_row(raw_rows: str) -> list[list[int]]:
    rows: list[str] = raw_rows.strip().split(" ")
    return [[card_map.get(char) or int(char) for char in row.strip()] for row in rows]


def parse_stack(raw_stack: str) -> list[int]:
    return [card_map.get(char) or int(char) for char in raw_stack]


raw_rows, raw_stack, known_min_moves = example_game_raw
rows = parse_row(raw_rows)
stack = parse_stack(raw_stack)

initial_board = Board(rows=rows, stack=stack)


# Allow top 3 moves for first 5 actions
first_top_moves = 3
first_games = 5
# Then fallback to 2
top_moves = 2


solution = simulate(
    initial_board,
    known_min_moves=known_min_moves,
    top_moves=top_moves,
    first_top_moves=first_top_moves,
    first_games=first_games,
)
describe_solution(initial_board, solution)
