# Mini Chess AI
# Minimax + Alpha-Beta Pruning

PIECE_VALUE = {
    'P': 1,
    'N': 3,
    'B': 3,
    'R': 5,
    'Q': 9,
    'K': 100
}

nodes = 0
pruned = 0


# -----------------------------
# Display Board
# -----------------------------
def display(board):
    print("\n  a b c d e f g h")

    for i, row in enumerate(board):
        print(8 - i, " ".join(row))

    print()


# -----------------------------
# Check Color
# -----------------------------
def color(piece):
    if piece == '.':
        return None

    if piece.isupper():
        return 'W'

    return 'B'


# -----------------------------
# Evaluation
# -----------------------------
def evaluate(board):

    score = 0

    for r in range(8):
        for c in range(8):

            piece = board[r][c]

            if piece == '.':
                continue

            # Material value
            value = PIECE_VALUE[piece.upper()]

            # Material score
            if piece.isupper():
                score += value
            else:
                score -= value

            # Positional bonus for controlling the center
            if 2 <= r <= 5 and 2 <= c <= 5:

                if piece.isupper():
                    score += 0.1
                else:
                    score -= 0.1

    return score


# -----------------------------
# Generate Moves
# -----------------------------
def generate_moves(board, player):

    moves = []

    directions = {
        'R': [(1,0), (-1,0), (0,1), (0,-1)],
        'B': [(1,1), (1,-1), (-1,1), (-1,-1)],
        'Q': [
            (1,0), (-1,0), (0,1), (0,-1),
            (1,1), (1,-1), (-1,1), (-1,-1)
        ],
        'K': [
            (1,0), (-1,0), (0,1), (0,-1),
            (1,1), (1,-1), (-1,1), (-1,-1)
        ],
        'N': [
            (2,1), (2,-1),
            (-2,1), (-2,-1),
            (1,2), (1,-2),
            (-1,2), (-1,-2)
        ]
    }

    for r in range(8):
        for c in range(8):

            piece = board[r][c]

            if color(piece) != player:
                continue

            p = piece.upper()

            # Pawn
            if p == 'P':

                direction = -1 if player == 'W' else 1

                nr = r + direction

                if 0 <= nr < 8 and board[nr][c] == '.':
                    moves.append((r, c, nr, c))

                for dc in [-1, 1]:

                    nc = c + dc

                    if 0 <= nr < 8 and 0 <= nc < 8:

                        if board[nr][nc] != '.' and \
                           color(board[nr][nc]) != player:

                            moves.append((r, c, nr, nc))

            # Other pieces
            elif p in directions:

                for dr, dc in directions[p]:

                    nr = r + dr
                    nc = c + dc

                    while 0 <= nr < 8 and 0 <= nc < 8:

                        target = board[nr][nc]

                        if target == '.':
                            moves.append(
                                (r, c, nr, nc)
                            )

                        else:

                            if color(target) != player:
                                moves.append(
                                    (r, c, nr, nc)
                                )

                            break

                        # King and Knight move only once
                        if p == 'K' or p == 'N':
                            break

                        nr += dr
                        nc += dc

    return moves


# -----------------------------
# Make Move
# -----------------------------
def make_move(board, move):

    new_board = [row[:] for row in board]

    r1, c1, r2, c2 = move

    new_board[r2][c2] = new_board[r1][c1]

    new_board[r1][c1] = '.'

    return new_board


# -----------------------------
# Minimax + Alpha-Beta
# -----------------------------
def minimax(board, depth, alpha, beta, maximizing):

    global nodes, pruned

    nodes += 1

    if depth == 0:
        return evaluate(board), None

    player = 'W' if maximizing else 'B'

    moves = generate_moves(board, player)

    if not moves:
        return evaluate(board), None

    best_move = moves[0]

    if maximizing:

        best_score = -float('inf')

        for move in moves:

            new_board = make_move(board, move)

            score, _ = minimax(
                new_board,
                depth - 1,
                alpha,
                beta,
                False
            )

            if score > best_score:
                best_score = score
                best_move = move

            alpha = max(alpha, best_score)

            if beta <= alpha:
                pruned += 1
                break

        return best_score, best_move

    else:

        best_score = float('inf')

        for move in moves:

            new_board = make_move(board, move)

            score, _ = minimax(
                new_board,
                depth - 1,
                alpha,
                beta,
                True
            )

            if score < best_score:
                best_score = score
                best_move = move

            beta = min(beta, best_score)

            if beta <= alpha:
                pruned += 1
                break

        return best_score, best_move


# -----------------------------
# Convert Move to Chess Notation
# -----------------------------
def move_name(move):

    files = "abcdefgh"

    r1, c1, r2, c2 = move

    return (
        files[c1] + str(8-r1) +
        files[c2] + str(8-r2)
    )


# -----------------------------
# Main Program
# -----------------------------
def main():

    global nodes, pruned

    board = [
        list("rnbqkbnr"),
        list("pppppppp"),
        list("........"),
        list("........"),
        list("........"),
        list("........"),
        list("PPPPPPPP"),
        list("RNBQKBNR")
    ]

    print("==============================")
    print("       MINI CHESS AI")
    print("==============================")

    try:
        depth = int(
            input("Enter AI search depth (1-3): ")
        )
    except:
        depth = 2

    if depth < 1:
        depth = 1

    if depth > 3:
        depth = 3

    print("\nInitial Board:")

    display(board)

    print("Searching...")

    nodes = 0
    pruned = 0

    score, best_move = minimax(
        board,
        depth,
        -float('inf'),
        float('inf'),
        False
    )

    print("\nAI Best Move:")

    if best_move:
        print(move_name(best_move))

    print("\nEvaluation:", score)

    print("Nodes searched:", nodes)

    print("Branches pruned:", pruned)

    print("\nSearch depth:", depth)

    print("\nProgram completed successfully.")


if __name__ == "__main__":
    main()