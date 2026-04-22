"""
Tests for the Config dataclass — default values and derived fields.
"""

from src.utils.config import Config


class TestConfig:
    def test_default_values(self) -> None:
        cfg = Config()
        assert cfg.WINDOW_WIDTH == 720
        assert cfg.WINDOW_HEIGHT == 700
        assert cfg.WINDOW_TITLE == "Tetris Clone"
        assert cfg.FPS == 60
        assert cfg.BOARD_COLS == 10
        assert cfg.BOARD_ROWS == 20
        assert cfg.CELL_SIZE == 30

    def test_derived_board_px_dimensions(self) -> None:
        cfg = Config()
        assert cfg.BOARD_PX_WIDTH == 10 * 30  # 300
        assert cfg.BOARD_PX_HEIGHT == 20 * 30  # 600

    def test_scoring_constants(self) -> None:
        cfg = Config()
        assert cfg.SCORE_SINGLE == 100
        assert cfg.SCORE_DOUBLE == 300
        assert cfg.SCORE_TRIPLE == 500
        assert cfg.SCORE_TETRIS == 800

    def test_gameplay_constants(self) -> None:
        cfg = Config()
        assert cfg.INITIAL_DROP_INTERVAL == 800
        assert cfg.LOCK_DELAY == 500
        assert cfg.LINES_PER_LEVEL == 10
        assert cfg.SPEED_INCREMENT == 0.8
        assert cfg.MIN_DROP_INTERVAL == 50
