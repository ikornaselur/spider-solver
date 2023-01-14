import copy
import time
from collections import Counter, defaultdict
from heapq import heappop as pop
from heapq import heappush as push

from rich.console import Console

from spider_solver.board import Board, card_from_raw, card_pos, pretty_card

console = Console()


def get_loc(board: Board, card: int) -> str:
    """Helper func to produce user friendly location info"""
    if card in board.cards:
        num_counts = Counter(card_from_raw(card) for card in board.leaves)
        if num_counts[card_from_raw(card)] == 1:
            return "[yellow]on the board[/yellow]"
        return f"[yellow]{card_pos(board.cards, card)}[/yellow]"
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
                f"[{board.moves + draws}] Remove [green]{pretty_card(cards[0])}[/green] {get_loc(board, cards[0])}"
            )
        else:
            # Why [1] before [0]? When you match board card with stack card [0]
            # is board and [1] is stack and it turns out that I always look
            # first at the stack when matching these cards.. so just swap them
            # here rather than in logic I guess
            console.print(
                f"[{board.moves + draws}] Match [green]{pretty_card(cards[1])}[/green] {get_loc(board, cards[1])} and "
                f"[green]{pretty_card(cards[0])}[/green] {get_loc(board, cards[0])}"
            )

        board.play_move((move_type, draws, cards))
    console.print(f"[{board.moves}] [green]All done!")


# It's turtles all the way
def ddict():
    return defaultdict(ddict)


def add_solution(
    trie: dict, moves_played: list[int], available_move_count: int, winning_state: int
):
    """Add board state to a solution trie

    Board state is not the full board state, as it can easily be reconstructed
    from the path, but rather just how many moves can be played at this state
    and if the state is a winning state.

    Number of moves is just an int from 0 to however many moves are available
    Winning state is:
        1 if winning state
        0 if unknown
        -1 if failed
        -2 if number of moves exceeded known min count
    """
    trie_node = trie
    for move in moves_played:
        trie_node = trie_node[move]

    trie_node["move_count"] = available_move_count
    trie_node["winning_state"] = winning_state


def simulate(
    initial_board: Board,
    *,
    known_min_moves: int,
    top_moves: int = 2,
    first_top_moves: int = 3,
    first_games: int = 5,
) -> tuple[list[int], dict]:
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

    solution_trie = ddict()  # trie-ish?

    now = time.time()

    while boards:
        _, moves_made, board = pop(boards)

        if board.moves > min_moves:
            console.log(
                f"[{time.time() - now:.02f}s] Testing games with {board.moves}/{known_min_moves} moves.. (total: {len(boards)}, dups: {dups})"
            )
            min_moves = board.moves

        if board.completed or not board.cards:
            console.print(f"[green]Solution found with {board.moves} moves")
            if board.moves < known_min_moves:
                console.print(
                    "[green bold]Found a solution less than previously known!"
                )
                add_solution(solution_trie, moves_made, 0, 1)
            elif board.moves == known_min_moves:
                console.print("[yellow]Found matching previously known!")
                add_solution(solution_trie, moves_made, 0, 1)
            else:
                console.print("[red bold]Couldn't find the best solution!")
                add_solution(solution_trie, moves_made, len(board.get_moves()), -2)
            return moves_made, solution_trie

        # Get all moves in sorted order, by lower movements required
        moves = sorted(board.get_moves(), key=lambda m: (m[1], str(m[2])))

        if not moves:
            add_solution(solution_trie, moves_made, 0, -1)
            continue

        add_solution(solution_trie, moves_made, len(moves), 0)

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

            if move[1] + board.moves > known_min_moves:
                # Moves will definitely go over the limit, no use playing it
                break

            # Hacky, whatever, will be slow!
            board_copy = copy.deepcopy(board)

            moves_played += 1
            board_copy.play_move(move)
            if (board_state := board_copy.state) in seen_states:
                dups += 1
                continue
            seen_states.add(board_state)

            entry = (board_copy.moves, moves_made + [idx + 1], board_copy)
            push(boards, entry)
    raise Exception("No solution found?")
