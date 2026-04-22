"""
Game state — tracks score, level, lines, and game-over status.

Separated from the Board class so that state logic is independently testable.
"""

from __future__ import annotations

from src.utils.config import Config


class GameState:
    """Mutable state that changes during gameplay."""

    def __init__(self, config: Config) -> None:
        self.config = config
        self.score: int = 0
        self.lines: int = 0
        self.level: int = 1
        self.game_over: bool = False
        self.paused: bool = False

    # ── Scoring ─────────────────────────────────────────────────────────

    def add_score(self, lines_cleared: int) -> None:
        """Update score and level based on how many lines were cleared."""
        if lines_cleared <= 0:
            return

        points = {
            1: self.config.SCORE_SINGLE,
            2: self.config.SCORE_DOUBLE,
            3: self.config.SCORE_TRIPLE,
            4: self.config.SCORE_TETRIS,
        }
        self.score += points.get(lines_cleared, 0) * self.level
        self.lines += lines_cleared

        # Level up every N lines
        self.level = (self.lines // self.config.LINES_PER_LEVEL) + 1

    # ── Drop speed ──────────────────────────────────────────────────────

    @property
    def drop_interval(self) -> int:
        """Current drop speed in milliseconds, clamped to minimum."""
        interval = int(
            self.config.INITIAL_DROP_INTERVAL
            * (self.config.SPEED_INCREMENT ** (self.level - 1))
        )
        return max(interval, self.config.MIN_DROP_INTERVAL)

    # ── State transitions ───────────────────────────────────────────────

    def toggle_pause(self) -> None:
        self.paused = not self.paused

    def end_game(self) -> None:
        self.game_over = True

    def reset(self) -> None:
        self.score = 0
        self.lines = 0
        self.level = 1
        self.game_over = False
        self.paused = False
