# Mini Chess AI - Extensions
# ------------------------------------------------------------
# NEW FILE. The original engine file is NOT modified.
# It is imported and reused (evaluate, generate_moves, make_move).
#
# New features:
#   1. Benchmark: search depth vs. speed, pruning effect
#   2. Move ordering (captures first) to improve alpha-beta pruning
#   3. AI vs AI self-play to show depth vs. playing strength
#   4. Human vs AI game (you play White)
#
# Put this file in the SAME folder as the original engine file.
# If your original file has a different name, change ENGINE_NAME.
# ------------------------------------------------------------

import importlib
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

ENGINE_NAME = "mini_chess_ai"   # original file name WITHOUT .py

try:
    engine = importlib.import_module(ENGINE_NAME)
except ModuleNotFoundError:
    raise SystemExit(
        "Original engine file '" + ENGINE_NAME + ".py' not found in this "
        "folder. Edit ENGINE_NAME at the top of extensions.py."
    )

FILES = "abcdefgh"


# -----------------------------
# Board helpers
# -----------------------------
def initial_board():
    return [
        list("rnbqkbnr"),
        list("pppppppp"),
        list("........"),
        list("........"),
        list("........"),
        list("........"),
        list("PPPPPPPP"),
        list("RNBQKBNR"),
    ]


def middlegame_board():
    """A test position with captures available (for pruning tests)."""
    board = initial_board()
    setup = [
        (6, 4, 4, 4),  # e2 -> e4
        (1, 3, 3, 3),  # d7 -> d5
        (7, 6, 5, 5),  # Ng1 -> f3
        (0, 2, 4, 6),  # Bc8 -> g4
        (7, 1, 5, 2),  # Nb1 -> c3
        (0, 6, 2, 5),  # Ng8 -> f6
    ]
    for move in setup:
        board = engine.make_move(board, move)
    return board


def winner(board):
    """Game ends when a king is captured (the base engine has no check)."""
    flat = "".join("".join(row) for row in board)
    if "k" not in flat:
        return "W"
    if "K" not in flat:
        return "B"
    return None


def parse_move(text):
    """'e2e3' -> (row1, col1, row2, col2), or None if invalid."""
    text = text.strip().lower().replace(" ", "")
    if len(text) != 4:
        return None
    f1, r1, f2, r2 = text
    if f1 not in FILES or f2 not in FILES:
        return None
    if r1 not in "12345678" or r2 not in "12345678":
        return None
    return (8 - int(r1), FILES.index(f1), 8 - int(r2), FILES.index(f2))


# -----------------------------
# Feature 2: Move ordering
# -----------------------------
def order_moves(board, moves):
    """Try captures first, best victim / cheapest attacker first.
    Good moves searched early -> more alpha-beta cutoffs."""
    values = engine.PIECE_VALUE

    def key(move):
        r1, c1, r2, c2 = move
        victim = board[r2][c2]
        if victim == ".":
            return 0
        attacker = board[r1][c1]
        return 10 * values[victim.upper()] - values[attacker.upper()]

    return sorted(moves, key=key, reverse=True)


# -----------------------------
# Search with switches (pruning / ordering)
# -----------------------------
def search(board, depth, alpha, beta, maximizing, stats,
           prune=True, order=True):
    stats["nodes"] += 1

    if depth == 0 or winner(board):
        return engine.evaluate(board), None

    player = "W" if maximizing else "B"
    moves = engine.generate_moves(board, player)

    if not moves:
        return engine.evaluate(board), None

    if order:
        moves = order_moves(board, moves)

    best_move = moves[0]
    best = -float("inf") if maximizing else float("inf")

    for move in moves:
        child = engine.make_move(board, move)
        score, _ = search(child, depth - 1, alpha, beta,
                          not maximizing, stats, prune, order)

        if maximizing:
            if score > best:
                best, best_move = score, move
            alpha = max(alpha, best)
        else:
            if score < best:
                best, best_move = score, move
            beta = min(beta, best)

        if prune and beta <= alpha:
            stats["pruned"] += 1
            break

    return best, best_move


def ai_move(board, player, depth, prune=True, order=True):
    """Returns (score, move, stats, seconds)."""
    stats = {"nodes": 0, "pruned": 0}
    start = time.time()
    score, move = search(board, depth, -float("inf"), float("inf"),
                         player == "W", stats, prune, order)
    return score, move, stats, time.time() - start


# -----------------------------
# Feature 1: Benchmark
# -----------------------------
def benchmark(max_depth=3):
    configs = [
        ("Minimax (no pruning)", False, False),
        ("Alpha-beta", True, False),
        ("Alpha-beta + ordering", True, True),
    ]
    positions = [
        ("Initial position", initial_board()),
        ("Middlegame position", middlegame_board()),
    ]

    for pos_name, board in positions:
        print("\n=== " + pos_name + " (White to move) ===")
        print("%-5s %-22s %9s %8s %8s %-6s %6s" %
              ("Depth", "Method", "Nodes", "Pruned", "Time(s)",
               "Move", "Score"))
        print("-" * 70)

        for depth in range(1, max_depth + 1):
            base_nodes = None
            for label, prune, order in configs:
                score, move, stats, secs = ai_move(
                    board, "W", depth, prune, order)
                if base_nodes is None:
                    base_nodes = stats["nodes"]
                saved = 100.0 * (1 - stats["nodes"] / base_nodes)
                print("%-5d %-22s %9d %8d %8.3f %-6s %6.1f  (-%.0f%% nodes)" %
                      (depth, label, stats["nodes"], stats["pruned"],
                       secs, engine.move_name(move) if move else "-",
                       score, saved))
            print()


# -----------------------------
# Feature 3: AI vs AI self-play
# -----------------------------
def self_play(white_depth=3, black_depth=1, max_moves=30):
    board = initial_board()
    player = "W"
    depths = {"W": white_depth, "B": black_depth}

    print("\nSelf-play: White depth %d vs Black depth %d (max %d moves each)"
          % (white_depth, black_depth, max_moves))

    for ply in range(max_moves * 2):
        score, move, stats, secs = ai_move(board, player, depths[player])
        if move is None:
            print("No legal moves for", player)
            break

        board = engine.make_move(board, move)
        print("%2d. %s plays %s  (eval %.1f, nodes %d, %.2fs)" %
              (ply // 2 + 1, player, engine.move_name(move),
               score, stats["nodes"], secs))

        if winner(board):
            break
        player = "B" if player == "W" else "W"

    engine.display(board)
    final = engine.evaluate(board)
    win = winner(board)

    if win:
        result = ("White" if win == "W" else "Black") + " wins (king captured)"
    elif final > 1:
        result = "White ahead on material/position"
    elif final < -1:
        result = "Black ahead on material/position"
    else:
        result = "Roughly equal"

    print("Final evaluation:", final)
    print("Result:", result)
    return result


# -----------------------------
# Feature 4: Human vs AI
# -----------------------------
def human_vs_ai(depth=2):
    board = initial_board()
    print("\nYou are White (UPPERCASE). Enter moves like e2e3. Type 'quit' to stop.")
    print("Note: pawns move one square at a time in this engine.")

    while True:
        engine.display(board)
        legal = engine.generate_moves(board, "W")
        if not legal:
            print("You have no legal moves.")
            break

        text = input("Your move: ").strip().lower()
        if text == "quit":
            break

        move = parse_move(text)
        if move is None or move not in legal:
            print("Illegal or invalid move. Try again.")
            continue

        board = engine.make_move(board, move)
        if winner(board):
            engine.display(board)
            print("You win!")
            break

        score, ai, stats, secs = ai_move(board, "B", depth)
        if ai is None:
            print("AI has no legal moves.")
            break

        board = engine.make_move(board, ai)
        print("AI plays %s (eval %.1f, nodes %d, %.2fs)" %
              (engine.move_name(ai), score, stats["nodes"], secs))

        if winner(board):
            engine.display(board)
            print("AI wins!")
            break


# -----------------------------
# Menu
# -----------------------------
def ask_int(prompt, default, low, high):
    try:
        value = int(input(prompt))
    except ValueError:
        return default
    return max(low, min(high, value))


def main():
    while True:
        print("\n==============================")
        print("   MINI CHESS AI - EXTENSIONS")
        print("==============================")
        print("1. Benchmark: depth vs speed + pruning effect")
        print("2. AI vs AI self-play (depth vs strength)")
        print("3. Human vs AI")
        print("4. Exit")

        choice = input("Choose (1-4): ").strip()

        if choice == "1":
            d = ask_int("Max depth (1-4, default 3): ", 3, 1, 4)
            benchmark(d)
        elif choice == "2":
            wd = ask_int("White depth (1-3, default 3): ", 3, 1, 3)
            bd = ask_int("Black depth (1-3, default 1): ", 1, 1, 3)
            self_play(wd, bd)
        elif choice == "3":
            d = ask_int("AI depth (1-3, default 2): ", 2, 1, 3)
            human_vs_ai(d)
        elif choice == "4":
            break
        else:
            print("Please enter 1, 2, 3 or 4.")


if __name__ == "__main__":
    main()
