"""
Game configuration constants.

Centralised configuration so all magic numbers live in one place.
Tweak these values to adjust gameplay feel, window size, and difficulty.
"""

from dataclasses import dataclass, field


@dataclass
class Config:
    """Application-wide settings for the Tetris clone."""

    # ── Display ──────────────────────────────────────────────────────────
    WINDOW_WIDTH: int = 720
    WINDOW_HEIGHT: int = 700
    WINDOW_TITLE: str = "Tetris Clone"
    FPS: int = 60

    # ── Board dimensions (cells) ─────────────────────────────────────────
    BOARD_COLS: int = 10
    BOARD_ROWS: int = 20
    BOARD_X_OFFSET: int = 180  # px from left edge (shifted right for hold panel)
    BOARD_Y_OFFSET: int = 50   # px from top edge
    CELL_SIZE: int = 30

    # ── Hold panel (left side) ───────────────────────────────────────────
    HOLD_PANEL_WIDTH: int = 130
    HOLD_PANEL_X: int = 25
    HOLD_PANEL_Y: int = BOARD_Y_OFFSET

    # ── Next piece panel (right side) ────────────────────────────────────
    PANEL_WIDTH: int = 150
    PANEL_X: int = BOARD_X_OFFSET + BOARD_COLS * CELL_SIZE + 20
    PANEL_Y: int = BOARD_Y_OFFSET

    # ── Gameplay ─────────────────────────────────────────────────────────
    INITIAL_DROP_INTERVAL: int = 800       # ms
    SOFT_DROP_INTERVAL: int = 50            # ms
    LOCK_DELAY: int = 500                   # ms before piece locks
    LINES_PER_LEVEL: int = 10
    SPEED_INCREMENT: float = 0.8            # multiplier per level
    MIN_DROP_INTERVAL: int = 50             # fastest possible speed

    # ── Scoring (classic NES-inspired) ──────────────────────────────────
    SCORE_SINGLE: int = 100
    SCORE_DOUBLE: int = 300
    SCORE_TRIPLE: int = 500
    SCORE_TETRIS: int = 800

    # ── Ghost piece ──────────────────────────────────────────────────────
    GHOST_ALPHA: int = 80  # 0–255

    # ── Grid lines ───────────────────────────────────────────────────────
    GRID_LINE_COLOR: tuple[int, int, int] = (40, 40, 40)

    # ── Derived sizes (computed in __post_init__) ───────────────────────
    BOARD_PX_WIDTH: int = field(init=False)
    BOARD_PX_HEIGHT: int = field(init=False)

    def __post_init__(self) -> None:
        self.BOARD_PX_WIDTH = self.BOARD_COLS * self.CELL_SIZE
        self.BOARD_PX_HEIGHT = self.BOARD_ROWS * self.CELL_SIZE
