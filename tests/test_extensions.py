# Tests for extensions.py
# Run from the project root:  pytest
# (needs: pip install pytest)

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "src"))

import extensions as ext   # noqa: E402


def empty_board():
    return [list("........") for _ in range(8)]


def test_parse_move_valid():
    assert ext.parse_move("e2e3") == (6, 4, 5, 4)


def test_parse_move_invalid():
    assert ext.parse_move("z9z9") is None
    assert ext.parse_move("e2") is None


def test_winner_detects_missing_king():
    board = ext.initial_board()
    assert ext.winner(board) is None
    board[0][4] = "."          # remove black king
    assert ext.winner(board) == "W"


def test_order_moves_puts_best_capture_first():
    board = empty_board()
    board[4][0] = "R"          # white rook
    board[4][5] = "q"          # black queen on same row
    moves = ext.engine.generate_moves(board, "W")
    ordered = ext.order_moves(board, moves)
    assert ordered[0] == (4, 0, 4, 5)


def test_pruning_and_ordering_do_not_change_score():
    board = ext.middlegame_board()
    for depth in (1, 2):
        plain = ext.ai_move(board, "W", depth, False, False)[0]
        pruned = ext.ai_move(board, "W", depth, True, False)[0]
        ordered = ext.ai_move(board, "W", depth, True, True)[0]
        assert plain == pruned == ordered


def test_pruning_reduces_nodes():
    board = ext.middlegame_board()
    plain = ext.ai_move(board, "W", 2, False, False)[2]["nodes"]
    pruned = ext.ai_move(board, "W", 2, True, True)[2]["nodes"]
    assert pruned < plain
