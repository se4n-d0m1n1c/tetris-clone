"""
Tests for GameState — scoring, level progression, drop speed, pause, reset.
"""

import pytest

from src.core.game_state import GameState
from src.utils.config import Config


@pytest.fixture
def state() -> GameState:
    return GameState(Config())


# ── Initialisation ────────────────────────────────────────────────────────

class TestGameStateInit:
    def test_defaults(self, state: GameState) -> None:
        assert state.score == 0
        assert state.lines == 0
        assert state.level == 1
        assert state.game_over is False
        assert state.paused is False


# ── Scoring ───────────────────────────────────────────────────────────────

class TestAddScore:
    def test_single_line_at_level_1(self, state: GameState) -> None:
        state.add_score(1)
        assert state.score == 100
        assert state.lines == 1

    def test_double_line(self, state: GameState) -> None:
        state.add_score(2)
        assert state.score == 300
        assert state.lines == 2

    def test_triple_line(self, state: GameState) -> None:
        state.add_score(3)
        assert state.score == 500
        assert state.lines == 3

    def test_tetris(self, state: GameState) -> None:
        state.add_score(4)
        assert state.score == 800
        assert state.lines == 4

    def test_zero_lines_does_nothing(self, state: GameState) -> None:
        state.add_score(0)
        assert state.score == 0
        assert state.lines == 0

    def test_negative_lines_does_nothing(self, state: GameState) -> None:
        state.add_score(-1)
        assert state.score == 0

    def test_unknown_line_count_uses_zero(self, state: GameState) -> None:
        state.add_score(5)
        assert state.score == 0  # 5 not in points dict
        assert state.lines == 5

    def test_score_multiplied_by_level(self, state: GameState) -> None:
        state.lines = 10
        state.level = 2  # simulate level-up
        state.add_score(1)
        assert state.score == 200  # 100 * 2
        assert state.lines == 11


# ── Level progression ─────────────────────────────────────────────────────

class TestLevelProgression:
    def test_level_2_after_10_lines(self, state: GameState) -> None:
        state.add_score(4)  # 4 lines
        state.add_score(4)  # 8 lines
        state.add_score(4)  # 12 lines
        assert state.level == 2  # lines//10 + 1 = 12//10 + 1 = 2

    def test_level_3_after_20_lines(self, state: GameState) -> None:
        for _ in range(5):
            state.add_score(4)
        assert state.level == 3

    def test_level_does_not_increase_below_threshold(self, state: GameState) -> None:
        state.add_score(4)  # 4 lines
        assert state.level == 1


# ── Drop interval ─────────────────────────────────────────────────────────

class TestDropInterval:
    def test_default_drop_interval(self, state: GameState) -> None:
        assert state.drop_interval == 800

    def test_faster_at_higher_level(self, state: GameState) -> None:
        state.level = 5
        expected = int(800 * (0.8 ** 4))
        assert state.drop_interval == expected

    def test_clamped_to_minimum(self, state: GameState) -> None:
        state.level = 100
        assert state.drop_interval == 50  # MIN_DROP_INTERVAL


# ── State transitions ─────────────────────────────────────────────────────

class TestTogglePause:
    def test_pauses_and_unpauses(self, state: GameState) -> None:
        assert state.paused is False
        state.toggle_pause()
        assert state.paused is True
        state.toggle_pause()
        assert state.paused is False


class TestEndGame:
    def test_sets_game_over(self, state: GameState) -> None:
        state.end_game()
        assert state.game_over is True


class TestReset:
    def test_resets_all_values(self, state: GameState) -> None:
        state.score = 5000
        state.lines = 42
        state.level = 5
        state.game_over = True
        state.paused = True

        state.reset()

        assert state.score == 0
        assert state.lines == 0
        assert state.level == 1
        assert state.game_over is False
        assert state.paused is False
