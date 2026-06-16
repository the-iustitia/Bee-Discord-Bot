import random

EMOJIS = ["🍎", "🍌", "🍇", "🍒", "🍍", "🥝", "🍉", "🍑"]


def generate_board():
    board = EMOJIS * 2
    random.shuffle(board)
    return board