# Chess Engine

- Currently ~**1700 Elo** (*Benchmarked against Chess.com engine).

## Tech Stack
- **Language**: C++17
- **GUI Library**: SFML (Simple and Fast Multimedia Library)

---

## File Structure

```text
├── assets/
│   └── pieces/            # Graphical PNG assets for chess pieces (wp, bp, wk, etc.)
├── src/
│   ├── main.cpp           # Program entry point
│   ├── engine/            # Chess rule validation and game loop
│   │   ├── ai/
│   │   │   ├── ai_board   # AI internal board representation & evaluation
│   │   │   └── ai_engine  # AI search & heuristic algorithms
│   │   ├── board      # Board state, moves, castling, en passant, signatures
│   │   ├── game       # Main game state manager, threads, draw logic
│   │   ├── move       # Move structure
│   │   ├── move_generator # Legal move generators
│   │   └── piece      # Piece types and colors
│   └── gui/               # Rendering and user input
│       ├── input_handler  # Mouse coordinate to square conversion
│       └── renderer       # SFML rendering functions for board, pieces, overlays
└── README.md              # This documentation file
```

---

## Prerequisites

To build the game, you need the SFML development library installed on your system.

### Windows (MSYS2 MinGW-w64)
Run the following command in the MSYS2 terminal:
```bash
pacman -S mingw-w64-x86_64-sfml
```

### macOS (Homebrew)
Run the following command:
```bash
brew install sfml
```

### Linux (Ubuntu/Debian)
Run the following command:
```bash
sudo apt-get install libsfml-dev
```

---

## Compilation

You can compile the project using standard G++ command line arguments.

### Windows (MSYS2 MinGW-w64)
Run the following command from the project root directory:
```powershell
C:\msys64\mingw64\bin\g++.exe -std=c++17 src/main.cpp src/gui/input_handler.cpp src/gui/renderer.cpp src/engine/board.cpp src/engine/game.cpp src/engine/piece.cpp src/engine/move_generator.cpp src/engine/ai/ai_board.cpp src/engine/ai/ai_engine.cpp -o chess.exe -lsfml-graphics -lsfml-window -lsfml-system
```

---

## How to Play

1. Run the compiled executable:
   ```bash
   ./chess.exe
   ```
2. **Main Menu**: Choose your opponent mode using the mouse or shortcuts `1`, `2`, or `3` on your keyboard.
3. **Game Over**:
   - Click **Play Again (R)** or press `R` to restart in the same mode.
   - Click **Main Menu (M)** or press `M` to go back to the menu screen.
