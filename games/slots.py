import random

FRUITS = ["🍎", "🍇", "🍒", "🍋", "🍉"]
BEE = "🐝"


def roll():
    r = random.random()

    if r < 0.01:
        return [BEE] * 5, "mega_win"

    if r < 0.11:
        f = random.choice(FRUITS)
        return [f] * 5, "win"

    return [random.choice(FRUITS + [BEE]) for _ in range(5)], "lose"


def evaluate(board):
    if board.count(BEE) == 5:
        return "mega_win"
    if len(set(board)) == 1:
        return "win"
    return "lose"