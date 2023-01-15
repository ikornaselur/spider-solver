from spider_solver.game import add_solution, ddict


def test_solution_trie_add_solution():
    solution_trie = ddict()

    add_solution(solution_trie, [], 3, 0)
    add_solution(solution_trie, [1], 1, 0)
    add_solution(solution_trie, [1, 1], 0, 1)
    add_solution(solution_trie, [2], 0, -1)
    add_solution(solution_trie, [3], 2, 0)
    add_solution(solution_trie, [3, 1], 1, 0)
    add_solution(solution_trie, [3, 1, 1], 2, -2)

    assert solution_trie["winning_state"] == 0
    assert solution_trie[1]["winning_state"] == 0
    assert solution_trie[1][1]["winning_state"] == 1
    assert solution_trie[2]["winning_state"] == -1
    assert solution_trie[3]["winning_state"] == 0
    assert solution_trie[3][1]["winning_state"] == 0
    assert solution_trie[3][1][1]["winning_state"] == -2

    assert solution_trie[1]['move_count'] == 1
    assert solution_trie[1][1]['move_count'] == 0
