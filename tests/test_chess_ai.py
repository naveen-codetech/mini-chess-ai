import sys
import os

# Allow Python to find the source file
sys.path.append(
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "src")
    )
)

from mini_chess_ai import evaluate, generate_moves, make_move


def starting_board():
    return [
        list("rnbqkbnr"),
        list("pppppppp"),
        list("........"),
        list("........"),
        list("........"),
        list("........"),
        list("PPPPPPPP"),
        list("RNBQKBNR")
    ]


def test_starting_position_evaluation():
    board = starting_board()

    assert evaluate(board) == 0


def test_white_has_moves():
    board = starting_board()

    moves = generate_moves(board, "W")

    assert len(moves) > 0


def test_black_has_moves():
    board = starting_board()

    moves = generate_moves(board, "B")

    assert len(moves) > 0


def test_make_move_changes_board():
    board = starting_board()

    move = (6, 4, 4, 4)

    new_board = make_move(board, move)

    assert new_board[6][4] == '.'
    assert new_board[4][4] == 'P'