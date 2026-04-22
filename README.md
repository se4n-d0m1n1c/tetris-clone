# Tetris Clone

A fully-featured Tetris clone built with **PyGame**, following industry-standard project structure and the official **Super Rotation System (SRS)** for piece rotation.

![Python](https://img.shields.io/badge/python-3.12-blue)
![PyGame](https://img.shields.io/badge/pygame-2.6-green)
![Tests](https://img.shields.io/badge/tests-77%20passing-brightgreen)

## Features

- **7 Standard Tetrominoes** — I, O, T, S, Z, J, L with proper colors
- **Super Rotation System (SRS)** — Full wall-kick tables for all pieces (4×4 tables for I-piece, 4×4 for JLSTZ)
- **Ghost Piece** — Translucent preview showing where the piece will land
- **Hold Mechanic** — Press **C** or **Left Shift** to hold a piece (one hold per spawn)
- **Next Piece Preview** — See what's coming up next
- **DAS Auto-Repeat** — Smooth, responsive left/right movement (167ms initial delay, 33ms repeat rate)
- **Classic Scoring** — 100/300/500/800 points for clearing 1/2/3/4 lines, multiplied by current level
- **Level Progression** — Level increases every 10 lines, drop speed gets faster (clamped 100–800ms)
- **Lock Delay** — 500ms lock delay when piece lands on a surface
- **Pause Menu** — Press **ESC** or **P** to pause (with Quit button)
- **Game Over Screen** — **R** to restart, **ESC** to quit

## Controls

| Action | Key |
|--------|-----|
| Move Left | Left Arrow |
| Move Right | Right Arrow |
| Soft Drop | Down Arrow |
| Hard Drop | Space |
| Rotate Clockwise | Up Arrow |
| Rotate Counter-Clockwise | Z or X |
| Hold Piece | C or Left Shift |
| Pause / Resume | ESC or P |
| Restart (on game over) | R |

## Project Structure

```
tetris-clone/
├── main.py                  # Entry point — initializes PyGame and runs the game loop
├── requirements.txt         # Python dependencies
├── .gitignore
├── README.md
├── src/
│   ├── __init__.py
│   ├── core/                # Core game logic (no PyGame dependency)
│   │   ├── __init__.py
│   │   ├── board.py         # Grid, collision detection, line clearing, ghost
│   │   ├── pieces.py        # Piece definitions, SRS rotation, wall-kick tables
│   │   └── game_state.py    # Score, level, lines, pause/game-over state
│   ├── game/                # Game orchestration
│   │   ├── __init__.py
│   │   ├── game_loop.py     # Main game loop — update, render, state transitions
│   │   └── input_handler.py # Keyboard input with DAS auto-repeat
│   ├── ui/                  # Rendering
│   │   ├── __init__.py
│   │   ├── renderer.py      # Draws board, pieces, panels, overlays
│   │   └── colors.py        # Color palette
│   └── utils/               # Utilities
│       ├── __init__.py
│       └── config.py        # Centralized configuration (all magic numbers)
└── tests/                   # Pytest test suite
    ├── __init__.py
    ├── test_board.py         # 30 tests — grid, collision, locking, line clearing, ghost
    ├── test_pieces.py        # 24 tests — rotation, wall kicks, shape data
    ├── test_game_state.py    # 17 tests — scoring, level progression, pause, reset
    └── test_config.py        # 6 tests — default values and derived constants
```

## Getting Started

### Prerequisites

- Python 3.12+
- pip

### Installation

```bash
# Clone the repository
git clone https://github.com/se4n-d0m1n1c/tetris-clone.git
cd tetris-clone

# Create a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Running the Game

```bash
source .venv/bin/activate
python3 main.py
```

### Running Tests

```bash
source .venv/bin/activate
pytest -v
```

All 77 tests should pass.

## Architecture

The project follows a clean separation of concerns:

- **`src/core/`** — Pure game logic with zero PyGame dependency. Board state, piece definitions, collision detection, and scoring are all framework-agnostic, making them easy to test and debug.
- **`src/game/`** — Orchestrates the game loop and handles input. The input handler implements DAS (Delayed Auto Shift) for responsive keyboard controls.
- **`src/ui/`** — All rendering logic. The renderer draws the board, pieces, ghost, hold panel, next piece preview, score display, and overlays.
- **`src/utils/config.py`** — A single dataclass holds every magic number (window size, cell size, timing constants, scoring values). Tweak anything without hunting through source files.
- **`tests/`** — Comprehensive test suite covering all core modules.

## Configuration

All gameplay and display constants are in `src/utils/config.py`:

```python
@dataclass
class Config:
    # Display
    WINDOW_WIDTH: int = 720
    WINDOW_HEIGHT: int = 700
    CELL_SIZE: int = 30
    BOARD_COLS: int = 10
    BOARD_ROWS: int = 20
    BOARD_X_OFFSET: int = 180
    BOARD_Y_OFFSET: int = 50

    # Timing
    DAS_DELAY: int = 167      # ms before auto-repeat starts
    DAS_RATE: int = 33        # ms between auto-repeat moves
    LOCK_DELAY: int = 500     # ms before piece locks

    # Scoring
    SCORE_SINGLE: int = 100
    SCORE_DOUBLE: int = 300
    SCORE_TRIPLE: int = 500
    SCORE_TETRIS: int = 800

    # Visual
    GHOST_ALPHA: int = 80
```

## License

This project is open source. Feel free to use, modify, and share.
