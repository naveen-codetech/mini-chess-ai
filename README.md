# Mini Chess AI

## 1. Problem Statement

Mini Chess AI is a small chess engine that uses Minimax with Alpha-Beta pruning to select a move. The program represents the chess board as an 8×8 grid, generates moves for the pieces, evaluates board positions using material values, and searches future positions to choose a move.

## 2. Objective

The objectives of this project are:

- Implement a chess board representation.
- Generate possible chess moves.
- Implement depth-limited Minimax.
- Implement Alpha-Beta pruning.
- Evaluate board positions using piece values.
- Count nodes searched and branches pruned.
- Compare different search depths.

## 3. AI Technique

The project uses **adversarial search**.

### Minimax

Minimax considers the AI as the maximizing player and the opponent as the minimizing player. The AI selects the move that gives the best evaluation assuming the opponent also chooses the best available response.

### Alpha-Beta Pruning

Alpha-Beta pruning avoids searching branches that cannot improve the final decision.

The evaluation follows:

```text
White material - Black material