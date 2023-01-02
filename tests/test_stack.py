from spider_solver.board import Card, MoveType, Stack


def test_stack_init():
    cards = [Card(i) for i in range(1, 5)]
    stack = Stack(cards)

    assert str(stack) == "<Stack 1 2 3 4>"


def test_stack_draw():
    cards = [Card(i) for i in range(1, 5)]
    stack = Stack(cards)

    card = stack.peek
    assert card.num == 1

    assert str(stack) == "<Stack 1 2 3 4>"

    card = stack.draw()
    assert card.num == 2

    assert str(stack) == "<Stack 2 3 4 1>"


def test_stack_num_in_stack():
    cards = [Card(i) for i in [1, 2, 5, 6, 2, 1]]
    stack = Stack(cards)

    assert stack.num_in_stack(1) == [0, 5]
    assert stack.num_in_stack(2) == [1, 4]
    assert stack.num_in_stack(3) == []
    assert stack.num_in_stack(4) == []
    assert stack.num_in_stack(5) == [2]
    assert stack.num_in_stack(6) == [3]


def test_stack_get_card_at_draws():
    cards = [Card(i) for i in [1, 2, 5, 6, 2, 1]]
    stack = Stack(cards)

    assert stack.get_card_at_draws(0).num == 1
    assert stack.get_card_at_draws(1).num == 2
    assert stack.get_card_at_draws(2).num == 5

    stack.draw()
    stack.draw()

    assert stack.get_card_at_draws(0).num == 5
    assert stack.get_card_at_draws(1).num == 6
    assert stack.get_card_at_draws(2).num == 2


def test_stack_get_stack_moves():
    cards = [Card(i) for i in [1, 2, 11, 2, 6, 1, 12, 5]]
    stack = Stack(cards)

    moves = stack.get_stack_moves()

    assert len(moves) == 3
    assert (MoveType.StackMatch, 2, (cards[1], cards[2])) in moves
    assert (MoveType.StackMatch, 3, (cards[2], cards[3])) in moves
    assert (MoveType.StackMatch, 6, (cards[5], cards[6])) in moves

    stack.draw()
    stack.draw()
    stack.draw()

    moves = stack.get_stack_moves()

    assert len(moves) == 3
    assert (MoveType.StackMatch, 7, (cards[1], cards[2])) in moves
    assert (MoveType.StackMatch, 0, (cards[2], cards[3])) in moves
    assert (MoveType.StackMatch, 3, (cards[5], cards[6])) in moves


def test_stack_get_stack_moves_with_a_king():
    cards = [Card(i) for i in [1, 2, 13, 4, 5, 13, 13, 6]]
    stack = Stack(cards)

    moves = stack.get_stack_moves()
    assert len(moves) == 3
    assert (MoveType.StackMatch, 2, (cards[2],)) in moves
    assert (MoveType.StackMatch, 5, (cards[5],)) in moves
    assert (MoveType.StackMatch, 6, (cards[6],)) in moves
