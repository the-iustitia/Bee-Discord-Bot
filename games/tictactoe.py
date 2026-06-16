import random

WIN_PATTERNS = [
    (0,1,2),(3,4,5),(6,7,8),
    (0,3,6),(1,4,7),(2,5,8),
    (0,4,8),(2,4,6)
]


def check_winner(board):
    for a,b,c in WIN_PATTERNS:
        if board[a] and board[a] == board[b] == board[c]:
            return board[a]
    return None


def empty_cells(board):
    return [i for i, v in enumerate(board) if v is None]


def bot_move(board):
    free = empty_cells(board)
    if not free:
        return None

    for i in free:
        b = board[:]
        b[i] = "O"
        if check_winner(b) == "O":
            return i

    for i in free:
        b = board[:]
        b[i] = "X"
        if check_winner(b) == "X":
            return i

    if board[4] is None:
        return 4

    corners = [0,2,6,8]
    free_corners = [c for c in corners if board[c] is None]
    if free_corners:
        return random.choice(free_corners)

    return random.choice(free)