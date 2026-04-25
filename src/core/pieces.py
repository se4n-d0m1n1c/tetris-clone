"""
Tetris piece definitions and rotation logic.

Each piece is defined as a list of rotation states.  Each rotation state is a
list of (row_offset, col_offset) tuples relative to the piece's pivot cell.
"""

from __future__ import annotations

from typing import ClassVar

import pygame

# ── Piece shapes ──────────────────────────────────────────────────────────
# Each shape is a list of rotation states.  Offsets are (row, col).
# The pivot is always at (0, 0) in the shape's local coordinate system.

SHAPES: dict[str, list[list[tuple[int, int]]]] = {
    "I": [
        [(0, -1), (0, 0), (0, 1), (0, 2)],
        [(-1, 0), (0, 0), (1, 0), (2, 0)],
        [(0, -1), (0, 0), (0, 1), (0, 2)],
        [(-1, 0), (0, 0), (1, 0), (2, 0)],
    ],
    "O": [
        [(0, 0), (0, 1), (1, 0), (1, 1)],
        [(0, 0), (0, 1), (1, 0), (1, 1)],
        [(0, 0), (0, 1), (1, 0), (1, 1)],
        [(0, 0), (0, 1), (1, 0), (1, 1)],
    ],
    "T": [
        [(0, -1), (0, 0), (0, 1), (1, 0)],
        [(-1, 0), (0, 0), (1, 0), (0, 1)],
        [(0, -1), (0, 0), (0, 1), (-1, 0)],
        [(-1, 0), (0, 0), (1, 0), (0, -1)],
    ],
    "S": [
        [(0, 0), (0, 1), (1, -1), (1, 0)],
        [(-1, 0), (0, 0), (0, 1), (1, 1)],
        [(0, 0), (0, 1), (1, -1), (1, 0)],
        [(-1, 0), (0, 0), (0, 1), (1, 1)],
    ],
    "Z": [
        [(0, -1), (0, 0), (1, 0), (1, 1)],
        [(-1, 1), (0, 0), (0, 1), (1, 0)],
        [(0, -1), (0, 0), (1, 0), (1, 1)],
        [(-1, 1), (0, 0), (0, 1), (1, 0)],
    ],
    "J": [
        [(0, -1), (0, 0), (0, 1), (1, -1)],
        [(-1, 0), (0, 0), (1, 0), (1, 1)],
        [(0, -1), (0, 0), (0, 1), (-1, 1)],
        [(-1, -1), (-1, 0), (0, 0), (1, 0)],
    ],
    "L": [
        [(0, -1), (0, 0), (0, 1), (1, 1)],
        [(-1, 0), (0, 0), (1, 0), (1, -1)],
        [(0, -1), (0, 0), (0, 1), (-1, -1)],
        [(-1, 1), (-1, 0), (0, 0), (1, 0)],
    ],
}

# ── Colours (one per piece type) ──────────────────────────────────────────
PIECE_COLORS: dict[str, pygame.Color] = {
    "I": pygame.Color("#00e5ff"),   # bright cyan
    "O": pygame.Color("#ffe74c"),   # bright yellow
    "T": pygame.Color("#d500f9"),   # neon purple
    "S": pygame.Color("#76ff03"),   # lime green
    "Z": pygame.Color("#ff1744"),   # bright red
    "J": pygame.Color("#ff9100"),   # bright orange
    "L": pygame.Color("#2979ff"),   # bright blue
}

# ── SRS wall-kick data ────────────────────────────────────────────────────
# Standard Rotation System kicks — offsets to try when a rotation fails.
# Key: (from_rotation, to_rotation).  Values: list of (row, col) kick offsets.
WALL_KICKS_JLSTZ: dict[tuple[int, int], list[tuple[int, int]]] = {
    (0, 1): [(0, 0), (0, -1), (-1, -1), (2, 0), (2, -1)],
    (1, 0): [(0, 0), (0, 1), (1, 1), (-2, 0), (-2, 1)],
    (1, 2): [(0, 0), (0, 1), (1, 1), (-2, 0), (-2, 1)],
    (2, 1): [(0, 0), (0, -1), (-1, -1), (2, 0), (2, -1)],
    (2, 3): [(0, 0), (0, 1), (-1, 1), (2, 0), (2, 1)],
    (3, 2): [(0, 0), (0, -1), (1, -1), (-2, 0), (-2, -1)],
    (3, 0): [(0, 0), (0, -1), (1, -1), (-2, 0), (-2, -1)],
    (0, 3): [(0, 0), (0, 1), (-1, 1), (2, 0), (2, 1)],
}

WALL_KICKS_I: dict[tuple[int, int], list[tuple[int, int]]] = {
    (0, 1): [(0, 0), (0, -2), (0, 1), (-1, -2), (2, 1)],
    (1, 0): [(0, 0), (0, 2), (0, -1), (1, 2), (-2, -1)],
    (1, 2): [(0, 0), (0, -1), (0, 2), (2, -1), (-1, 2)],
    (2, 1): [(0, 0), (0, 1), (0, -2), (-2, 1), (1, -2)],
    (2, 3): [(0, 0), (0, 2), (0, -1), (1, 2), (-2, -1)],
    (3, 2): [(0, 0), (0, -2), (0, 1), (-1, -2), (2, 1)],
    (3, 0): [(0, 0), (0, 1), (0, -2), (-2, 1), (1, -2)],
    (0, 3): [(0, 0), (0, -1), (0, 2), (2, -1), (-1, 2)],
}

PIECE_NAMES: list[str] = ["I", "O", "T", "S", "Z", "J", "L"]

# ── Spawn rotations ─────────────────────────────────────────────────────
# Fixed rotation for each piece type at spawn (0-3)
SPAWN_ROTATION: dict[str, int] = {
    "I": 0,   # horizontal bar
    "O": 0,   # square (all rotations same)
    "T": 0,   # stem up (flat bottom)
    "S": 0,   # laying down
    "Z": 0,   # laying down
    "J": 0,   # 3-block bottom, hook top-right
    "L": 0,   # 3-block bottom, hook top-left
}


class Piece:
    """A single Tetris piece with position, rotation state, and type."""

    def __init__(self, name: str, row: int, col: int) -> None:
        self.name: str = name
        self.row: int = row
        self.col: int = col
        self.rotation: int = 0

    # ── Properties ───────────────────────────────────────────────────────

    @property
    def cells(self) -> list[tuple[int, int]]:
        """Absolute board coordinates of this piece's filled cells."""
        offsets = SHAPES[self.name][self.rotation]
        return [(self.row + dr, self.col + dc) for dr, dc in offsets]

    @property
    def color(self) -> pygame.Color:
        return PIECE_COLORS[self.name]

    # ── Rotation ─────────────────────────────────────────────────────────

    def get_rotated_cells(self, direction: int = 1) -> list[tuple[int, int]]:
        """Return the cells if the piece were rotated *without* kicking."""
        new_rot = (self.rotation + direction) % 4
        offsets = SHAPES[self.name][new_rot]
        return [(self.row + dr, self.col + dc) for dr, dc in offsets]

    def get_wall_kicks(
        self, direction: int = 1,
    ) -> list[tuple[int, int]]:
        """Return the list of (row, col) kicks to try for a rotation."""
        from_rot = self.rotation
        to_rot = (self.rotation + direction) % 4
        key = (from_rot, to_rot)

        if self.name == "I":
            return WALL_KICKS_I.get(key, [(0, 0)])
        if self.name == "O":
            return [(0, 0)]
        return WALL_KICKS_JLSTZ.get(key, [(0, 0)])

    # ── Movement helpers ─────────────────────────────────────────────────

    def get_moved_cells(self, dr: int, dc: int) -> list[tuple[int, int]]:
        """Cells if the piece were shifted by (dr, dc)."""
        offsets = SHAPES[self.name][self.rotation]
        return [(self.row + dr + offset_r, self.col + dc + offset_c)
                for offset_r, offset_c in offsets]

    def __repr__(self) -> str:
        return f"Piece({self.name}, r={self.row}, c={self.col}, rot={self.rotation})"
