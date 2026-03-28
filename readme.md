# Chess (Python + Pygame)

A simple chess game built in **Python** with a **Pygame** UI. It supports playing chess with move validation and includes logic to compute a **best move** for the current position.

---

## Features

- Interactive **Pygame** chess UI
- Board representation + piece positions
- **Move validation**
- **Position evaluation**
- **Best-move search** (engine-style move selection)
- Game notation logging to a text file

---

## Project Structure

- `main.py` — Entry point; starts the game
- `chess_ui.py` — UI layer; handles user input/moves and calls best-move logic
- `board.py` — Board representation and piece positions
- `best_move.py` — Finds the best move for the current position (uses evaluation + move generation)
- `eval.py` — Returns an integer evaluation of the current position
- `valid_move.py` — Move validation utilities
- `check_detector.py` — Detects check conditions
- `mate_detector.py` — Detects checkmate conditions
- `three_repetition.py` — Threefold repetition detection
- `fifty_move_check.py` — Fifty-move rule detection
- `notation_convert.py` — Converts moves to/from chess notation formats
- `find_opening_move.py` — Opening-related move selection (if applicable)
- `game.txt` — Stores the game played so far (notation + string form)
- `images/` — Assets used by the UI (pieces/board images)
- `opening/`, `moves/` — Data folders used by the engine/opening logic

---

## Requirements

- Python 3.x
- `pygame`

## How to Run

From the repository root:

```bash
python main.py
```

This will open the Pygame window and start the chess UI.

---

## How the “Best Move” Works

The engine flow is roughly:

1. Generate / validate legal moves
2. Evaluate resulting positions (`eval.py`)
3. Choose the best scoring move (`best_move.py`)
4. UI applies the move and continues (`chess_ui.py`)
