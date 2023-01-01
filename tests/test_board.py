from spider_solver.board import Board, Card, Stack


def test_card_init():
    card = Card(13)

    assert str(card) == "<Card _<-K->_>"


def test_card_dependant():
    left = Card(10)
    card = Card(7, left=left)

    assert str(card) == "<Card 10<-7->_>"


def test_card_parent():
    left = Card(10)
    card = Card(7, left=left)

    assert left.parent == card


def test_stack_init():
    cards = [Card(i) for i in range(1, 5)]
    stack = Stack(cards)

    assert str(stack) == "<Stack 1 2 3 4>"


def test_stack_draw():
    cards = [Card(i) for i in range(1, 5)]
    stack = Stack(cards)

    card = stack.peek()
    assert card.num == 1

    assert str(stack) == "<Stack 1 2 3 4>"

    card = stack.draw()
    assert card.num == 2

    assert str(stack) == "<Stack 2 3 4 1>"


def test_board_from_ints():
    board = Board.from_ints(
        rows=[
            [1],
            [1, 2],
            [1, 2, 3],
            [1, 2, 3, 4],
            [1, 2, 3, 4, 5],
            [1, 2, 3, 4, 5, 6],
            [1, 2, 3, 4, 5, 6, 7],
        ],
        stack=[1, 2, 3, 4],
    )

    assert board.card_root is not None
    assert board.card_root.num == 1
    assert board.card_root.left is not None
    assert board.card_root.left.num == 1
    assert board.card_root.right is not None
    assert board.card_root.right.num == 2

    left = board.card_root.left
    right = board.card_root.right

    assert left.parent is not None
    assert left.parent.right == right
