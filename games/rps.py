import random

CHOICES = ["rock", "paper", "scissors"]

WIN_MAP = {
    "rock": "scissors",
    "paper": "rock",
    "scissors": "paper"
}


def result(a, b):
    if a == b:
        return "draw"
    if WIN_MAP[a] == b:
        return "win"
    return "lose"


def bot_choice():
    return random.choice(CHOICES)