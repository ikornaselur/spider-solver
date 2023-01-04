import copy
from collections import Counter
from heapq import heappop as pop
from heapq import heappush as push

from rich.console import Console

from spider_solver.board import Board, Card

console = Console()


def get_loc(board: Board, card: Card) -> str:
    """Helper func to produce user friendly location info"""
    if card.on_board:
        num_counts = Counter(card.num for card in board.leaves)
        if num_counts[card.num] == 1:
            return "[yellow]on the board[/yellow]"
        return f"[yellow]{card.pos.lower()}[/yellow]"
    else:
        return "[red]on the stack[/red]"


def describe_solution(board: Board, solution: list[int]) -> None:
    """Go through the solution and print out user friendly moves"""
    while solution:
        moves = sorted(board.get_moves(), key=lambda m: (m[1], str(m[2])))
        move_type, draws, cards = moves[solution.pop(0) - 1]  # 1-based to 0-based

        if draws:
            console.print(
                f"[{board.moves}] Draw {draws} card{'s' if draws > 1 else ''}"
            )
        if len(cards) == 1:
            console.print(
                f"[{board.moves + draws}] Remove [green]{cards[0].value}[/green] {get_loc(board, cards[0])}"
            )
        else:
            # Why [1] before [0]? When you match board card with stack card [0]
            # is board and [1] is stack and it turns out that I always look
            # first at the stack when matching these cards.. so just swap them
            # here rather than in logic I guess
            console.print(
                f"[{board.moves + draws}] Match [green]{cards[1].value}[/green] {get_loc(board, cards[1])} and "
                f"[green]{cards[0].value}[/green] {get_loc(board, cards[0])}"
            )

        board.play_move((move_type, draws, cards))
    console.print(f"[{board.moves}] [green]All done!")


def simulate(
    initial_board: Board,
    *,
    known_min_moves: int,
    top_moves: int = 2,
    first_top_moves: int = 3,
    first_games: int = 5,
) -> list[int]:
    """Simulate a board until a solution is found with the least amount of moves required

    known_min_moves: The current high score, used to optimise to not schedule
                     moves that would go over the known min moves. If not know,
                     could be set to something high, such as just 100
    top_moves:       How many moves to play per round of the game out of the possible moves.
                     Whenever there are more than 'top_moves' moves available
                     that require 0 cards being drawn, they are all played. If
                     there are less, it's limited by 'top_moves'
                     [Default: 2]
    first_top_moves: How many moves to play in the first few games, good to
                     play more options in the beginning
                     [Default: 3]
    first_games:     How many moves into the game to play the extra `first_top_moves`.
                     If `first_games` is 5 and `first_top_moves` is 3, then we'll simulate
                     the top 3 moves of every round until the games have made
                     at least 5 moves in total, where it will start simulating
                     just `top_moves` moves
                     [Default: 5]

    If solution is not found with the defaults, increasing either
    `first_top_moves` to 4-5 OR `first_games` to ~10 seems to work okay
    """
    # Brute forcing by copying so much is a bad idea, but hey, it works? Gotta start somewhere

    # Just stuff for logging
    dups = 0
    max_no_draw_moves = 0
    min_moves = 0

    # Track states for de-duplication
    seen_states = set()

    # The heap ordered by current moves
    boards = [(0, [], initial_board)]

    while boards:
        _, moves_made, board = pop(boards)
        if board.moves > min_moves:
            console.log(
                f"Testing games with {board.moves}/{known_min_moves} moves.. (total: {len(boards)}, dups: {dups})"
            )
            min_moves = board.moves

        if not board.cards:
            console.print(f"[green]Solution found with {board.moves} moves")
            if board.moves < known_min_moves:
                console.print(
                    "[green bold]Found a solution less than previously known!"
                )
            elif board.moves == known_min_moves:
                console.print("[yellow]Found matching previously known!")
            else:
                console.print("[red bold]Couldn't find the best solution!")
            return moves_made

        # Get all moves in sorted order, by lower movements required
        moves = sorted(board.get_moves(), key=lambda m: (m[1], str(m[2])))
        if not moves:
            continue
        no_draw_moves = len([m for m in moves if m[1] == 0])
        if no_draw_moves > max_no_draw_moves:
            max_no_draw_moves = no_draw_moves

        if board.moves <= first_games:
            max_moves = first_top_moves
        else:
            max_moves = top_moves

        # Always play all no draw moves
        moves_played = 0
        for idx, move in enumerate(moves):
            # for idx in range(min(len(moves), max_moves)):
            if move[1] > 0 and moves_played > max_moves:
                break
            # Hacky, whatever, will be slow!
            # TODO: Can we break the whole state down to a simpler data structure?
            board_copy = copy.deepcopy(board)
            copied_moves = sorted(
                board_copy.get_moves(), key=lambda m: (m[1], str(m[2]))
            )

            if copied_moves[idx][1] + board_copy.moves > known_min_moves:
                # Moves will definitely go over the limit, no use playing it
                break

            moves_played += 1
            board_copy.play_move(copied_moves[idx])
            if (board_state := board_copy.state) in seen_states:
                dups += 1
                continue
            seen_states.add(board_state)

            entry = (board_copy.moves, moves_made + [idx + 1], board_copy)
            push(boards, entry)
    raise Exception("No solution found?")
