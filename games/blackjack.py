import random

def draw():
    card = random.randint(2, 11)
    return card


def calculate(hand):
    total = sum(hand)

    # упрощённый Ace (11 -> 1 если перебор)
    if total > 21 and 11 in hand:
        hand = hand.copy()
        hand[hand.index(11)] = 1
        total = sum(hand)

    return total


def dealer_play(dealer):
    while calculate(dealer) < 17:
        dealer.append(draw())
    return dealer


def get_result(player, dealer):
    ps = calculate(player)
    ds = calculate(dealer)

    if ps > 21:
        return "lose"
    if ds > 21:
        return "win"
    if ps > ds:
        return "win"
    if ps < ds:
        return "lose"
    return "draw"