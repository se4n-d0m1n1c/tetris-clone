"""
Tests for the Piece class — shapes, cells, rotation, wall kicks, movement.
"""

import pytest
import pygame

from src.core.pieces import (
    Piece,
    SHAPES,
    PIECE_COLORS,
    PIECE_NAMES,
    WALL_KICKS_I,
    WALL_KICKS_JLSTZ,
)


# ── Initialisation ────────────────────────────────────────────────────────

class TestPieceInit:
    def test_creates_piece_with_defaults(self) -> None:
        p = Piece("T", row=5, col=3)
        assert p.name == "T"
        assert p.row == 5
        assert p.col == 3
        assert p.rotation == 0

    def test_repr(self) -> None:
        p = Piece("I", row=1, col=2)
        assert repr(p) == "Piece(I, r=1, c=2, rot=0)"


# ── Cells property ────────────────────────────────────────────────────────

class TestCells:
    def test_cells_match_rotation_zero(self) -> None:
        p = Piece("T", row=10, col=5)
        cells = p.cells
        # T rotation 0: (0,-1), (0,0), (0,1), (1,0)
        assert cells == [(10, 4), (10, 5), (10, 6), (11, 5)]

    def test_cells_after_rotation(self) -> None:
        p = Piece("T", row=10, col=5)
        p.rotation = 1
        cells = p.cells
        # T rotation 1: (-1,0), (0,0), (1,0), (0,1)
        assert cells == [(9, 5), (10, 5), (11, 5), (10, 6)]

    def test_cells_for_all_piece_names(self) -> None:
        for name in PIECE_NAMES:
            p = Piece(name, row=0, col=0)
            cells = p.cells
            assert len(cells) == 4
            # Every cell should be unique (no overlapping)
            assert len(set(cells)) == 4


# ── Color property ────────────────────────────────────────────────────────

class TestColor:
    def test_color_matches_piece_type(self) -> None:
        for name in PIECE_NAMES:
            p = Piece(name, row=0, col=0)
            assert p.color == PIECE_COLORS[name]

    def test_color_is_pygame_color(self) -> None:
        p = Piece("I", row=0, col=0)
        assert isinstance(p.color, pygame.Color)


# ── Rotation helpers ──────────────────────────────────────────────────────

class TestGetRotatedCells:
    def test_clockwise_rotation(self) -> None:
        p = Piece("T", row=10, col=5)
        rotated = p.get_rotated_cells(direction=1)
        # rotation 1: (-1,0), (0,0), (1,0), (0,1)
        assert rotated == [(9, 5), (10, 5), (11, 5), (10, 6)]

    def test_counter_clockwise_rotation(self) -> None:
        p = Piece("T", row=10, col=5)
        rotated = p.get_rotated_cells(direction=-1)
        # rotation 3 (counter-clockwise): (-1,0), (0,0), (1,0), (0,-1)
        assert rotated == [(9, 5), (10, 5), (11, 5), (10, 4)]

    def test_original_unchanged_after_get_rotated_cells(self) -> None:
        p = Piece("T", row=10, col=5)
        _ = p.get_rotated_cells(1)
        assert p.rotation == 0  # should not mutate


# ── Wall kicks ────────────────────────────────────────────────────────────

class TestGetWallKicks:
    def test_first_kick_is_always_no_offset(self) -> None:
        p = Piece("T", row=10, col=5)
        kicks = p.get_wall_kicks(1)
        assert kicks[0] == (0, 0)

    def test_i_piece_uses_separate_table(self) -> None:
        p = Piece("I", row=10, col=5)
        kicks = p.get_wall_kicks(1)
        assert kicks == WALL_KICKS_I[(0, 1)]

    def test_o_piece_has_no_kicks(self) -> None:
        p = Piece("O", row=10, col=5)
        kicks = p.get_wall_kicks(1)
        assert kicks == [(0, 0)]

    def test_jlstz_use_shared_table(self) -> None:
        for name in ["J", "L", "S", "T", "Z"]:
            p = Piece(name, row=10, col=5)
            kicks = p.get_wall_kicks(1)
            assert kicks == WALL_KICKS_JLSTZ[(0, 1)]

    def test_kicks_for_counter_clockwise(self) -> None:
        p = Piece("T", row=10, col=5)
        p.rotation = 1
        kicks = p.get_wall_kicks(-1)  # rotation 1 -> 0
        assert kicks == WALL_KICKS_JLSTZ[(1, 0)]

    def test_kicks_all_have_five_entries(self) -> None:
        for key, kicks in WALL_KICKS_I.items():
            assert len(kicks) == 5, f"I kick {key} has {len(kicks)} entries"
        for key, kicks in WALL_KICKS_JLSTZ.items():
            assert len(kicks) == 5, f"JLSTZ kick {key} has {len(kicks)} entries"


# ── Movement helper ───────────────────────────────────────────────────────

class TestGetMovedCells:
    def test_move_down(self) -> None:
        p = Piece("T", row=10, col=5)
        moved = p.get_moved_cells(1, 0)
        # T rotation 0: (0,-1),(0,0),(0,1),(1,0) -> shifted down by 1
        assert moved == [(11, 4), (11, 5), (11, 6), (12, 5)]

    def test_move_left(self) -> None:
        p = Piece("T", row=10, col=5)
        moved = p.get_moved_cells(0, -1)
        assert moved == [(10, 3), (10, 4), (10, 5), (11, 4)]

    def test_original_unchanged_after_get_moved_cells(self) -> None:
        p = Piece("T", row=10, col=5)
        _ = p.get_moved_cells(5, 5)
        assert p.row == 10
        assert p.col == 5


# ── Shape data integrity ──────────────────────────────────────────────────

class TestShapeData:
    def test_all_shapes_have_four_rotation_states(self) -> None:
        for name, states in SHAPES.items():
            assert len(states) == 4, f"{name} has {len(states)} rotations"

    def test_each_rotation_has_four_cells(self) -> None:
        for name, states in SHAPES.items():
            for i, state in enumerate(states):
                assert len(state) == 4, f"{name} rotation {i} has {len(state)} cells"

    def test_all_piece_names_have_shapes(self) -> None:
        assert set(SHAPES.keys()) == set(PIECE_NAMES)

    def test_all_piece_names_have_colors(self) -> None:
        assert set(PIECE_COLORS.keys()) == set(PIECE_NAMES)

    def test_wall_kick_tables_cover_all_transitions(self) -> None:
        """Every rotation transition should have an entry in the kick tables."""
        expected_transitions = {(0, 1), (1, 0), (1, 2), (2, 1), (2, 3), (3, 2), (3, 0), (0, 3)}
        assert set(WALL_KICKS_JLSTZ.keys()) == expected_transitions
        assert set(WALL_KICKS_I.keys()) == expected_transitions
