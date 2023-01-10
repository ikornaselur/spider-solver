from spider_solver.board import Card, MoveType, Stack


def test_stack_init():
    cards: list[Card | None] = [Card(i) for i in range(1, 5)]
    stack = Stack(cards)

    assert str(stack) == "<Stack 1 2 3 4 X>"


def test_stack_draw():
    cards: list[Card | None] = [Card(i) for i in range(1, 5)]
    stack = Stack(cards)

    card = stack.peek
    assert card
    assert card.num == 1

    assert str(stack) == "<Stack 1 2 3 4 X>"

    card = stack.draw()
    assert card
    assert card.num == 2

    assert str(stack) == "<Stack 2 3 4 X 1>"


def test_stack_draw_last_as_none():
    cards: list[Card | None] = [Card(i) for i in [1, 2, 3]]
    stack = Stack(cards)

    stack.draw(2)
    assert stack.prev is not None
    assert stack.prev.num == 2
    assert stack.peek is not None
    assert stack.peek.num == 3

    stack.draw()
    assert stack.prev is not None
    assert stack.prev.num == 3
    assert stack.peek is None


def test_stack_num_in_stack():
    cards: list[Card | None] = [
        Card(i) for i in [1, 2, 5, 6, 2, 1]
    ]
    stack = Stack(cards)

    assert stack.num_in_stack(1) == [0, 5]
    assert stack.num_in_stack(2) == [1, 4]
    assert stack.num_in_stack(3) == []
    assert stack.num_in_stack(4) == []
    assert stack.num_in_stack(5) == [2]
    assert stack.num_in_stack(6) == [3]


def test_stack_get_card_at_draws():
    cards: list[Card | None] = [
        Card(i) for i in [1, 2, 5, 6, 2, 1]
    ]
    stack = Stack(cards)

    card = stack.get_card_at_draws(0)
    assert card is not None
    assert card.num == 1
    card = stack.get_card_at_draws(1)
    assert card is not None
    assert card.num == 2
    card = stack.get_card_at_draws(2)
    assert card is not None
    assert card.num == 5

    stack.draw(2)

    card = stack.get_card_at_draws(0)
    assert card is not None
    assert card.num == 5
    card = stack.get_card_at_draws(1)
    assert card is not None
    assert card.num == 6
    card = stack.get_card_at_draws(2)
    assert card is not None
    assert card.num == 2


def test_stack_get_stack_moves():
    cards: list[Card | None] = [
        Card(i) for i in [1, 2, 11, 2, 6, 1, 12, 5]
    ]
    stack = Stack(cards)

    moves = stack.get_stack_moves()

    assert len(moves) == 3
    assert (MoveType.StackMatch, 2, (cards[1], cards[2])) in moves
    assert (MoveType.StackMatch, 3, (cards[2], cards[3])) in moves
    assert (MoveType.StackMatch, 6, (cards[5], cards[6])) in moves

    stack.draw(3)

    moves = stack.get_stack_moves()

    assert len(moves) == 3
    assert (MoveType.StackMatch, 8, (cards[1], cards[2])) in moves
    assert (MoveType.StackMatch, 0, (cards[2], cards[3])) in moves
    assert (MoveType.StackMatch, 3, (cards[5], cards[6])) in moves


def test_stack_get_stack_moves_with_a_king():
    cards: list[Card | None] = [
        Card(i) for i in [1, 2, 13, 4, 5, 13, 13, 6]
    ]
    stack = Stack(cards)

    moves = stack.get_stack_moves()
    assert len(moves) == 3
    assert (MoveType.StackMatch, 2, (cards[2],)) in moves
    assert (MoveType.StackMatch, 5, (cards[5],)) in moves
    assert (MoveType.StackMatch, 6, (cards[6],)) in moves


def test_stack_remove_card():
    cards: list[Card | None] = [
        Card(i) for i in [1, 2, 3, 4, 5, 6]
    ]
    stack = Stack(cards)

    assert str(stack) == "<Stack 1 2 3 4 5 6 X>"
    assert stack.peek is not None
    assert stack.peek.num == 1
    assert stack.prev is None

    # Remove the top card
    card = stack.get_card_at_draws(0)
    assert card is not None
    stack.remove_cards(card)

    assert str(stack) == "<Stack 2 3 4 5 6 X>"
    assert stack.peek is not None
    assert stack.peek.num == 2
    assert stack.prev is None

    stack.draw(2)

    assert str(stack) == "<Stack 4 5 6 X 2 3>"

    assert stack.peek is not None
    assert stack.peek.num == 4
    assert stack.prev is not None
    assert stack.prev.num == 3

    # Remove the three, which is at the "back of the stack", but is actually still visible in the game
    card = stack.get_card_at_draws(5)  # fifth draw is to reset the deck
    assert card is not None
    assert card.num == 3
    stack.remove_cards(card)

    assert str(stack) == "<Stack 4 5 6 X 2>"
    assert stack.peek is not None
    assert stack.peek.num == 4
    assert stack.prev is not None
    assert stack.prev.num == 2


def test_stack_remove_all_cards():
    cards: list[Card | None] = [Card(i) for i in [1, 2, 3]]
    stack = Stack(cards)

    assert str(stack) == "<Stack 1 2 3 X>"

    # Draw two, for reasons
    stack.draw(2)

    assert str(stack) == "<Stack 3 X 1 2>"

    # Let's start removing
    assert stack.peek is not None
    stack.remove_cards(stack.peek)

    assert str(stack) == "<Stack X 1 2>"

    assert stack.peek is None
    assert stack.prev is not None
    assert stack.prev.num == 2

    stack.draw()

    assert str(stack) == "<Stack 1 2 X>"

    assert stack.prev is None
    assert stack.peek.num == 1

    stack.draw()

    assert str(stack) == "<Stack 2 X 1>"
    assert stack.prev is not None
    assert stack.prev.num == 1
    assert stack.peek is not None
    assert stack.peek.num == 2

    stack.remove_cards([stack.prev, stack.peek])

    assert str(stack) == "<Stack X>"
