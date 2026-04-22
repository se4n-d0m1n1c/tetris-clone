"""
Game board — manages the grid, collision detection, and line clearing.
"""

from __future__ import annotations

import random

from src.core.pieces import SHAPES, Piece, PIECE_NAMES


class Board:
    """The Tetris play field: a 2-D grid of colour values (None = empty)."""

    def __init__(self, rows: int, cols: int) -> None:
        self.rows: int = rows
        self.cols: int = cols
        self.grid: list[list[tuple[int, int, int] | None]] = [
            [None] * cols for _ in range(rows)
        ]

    # ── Coordinate helpers ──────────────────────────────────────────────

    def is_in_bounds(self, row: int, col: int) -> bool:
        """Check if a cell is within the board boundaries."""
        return 0 <= row < self.rows and 0 <= col < self.cols

    def is_cell_empty(self, row: int, col: int) -> bool:
        """Check if a cell is within bounds AND unoccupied."""
        if not self.is_in_bounds(row, col):
            return False
        return self.grid[row][col] is None

    # ── Collision detection ─────────────────────────────────────────────

    def is_valid_position(self, cells: list[tuple[int, int]]) -> bool:
        """Return True if *all* given cells are in bounds and empty."""
        for row, col in cells:
            if not self.is_in_bounds(row, col):
                return False
            if not self.is_cell_empty(row, col):
                return False
        return True

    # ── Piece locking ───────────────────────────────────────────────────

    def lock_piece(self, piece: Piece) -> None:
        """Write the piece's cells into the grid permanently."""
        for row, col in piece.cells:
            if self.is_in_bounds(row, col):
                self.grid[row][col] = piece.color

    # ── Line clearing ───────────────────────────────────────────────────

    def get_full_rows(self) -> list[int]:
        """Return indices of completely filled rows (top-to-bottom order)."""
        return [
            row for row in range(self.rows)
            if all(cell is not None for cell in self.grid[row])
        ]

    def clear_rows(self, rows: list[int]) -> int:
        """Remove the given row indices and shift everything above down.

        Returns the number of rows cleared.
        """
        if not rows:
            return 0

        # Remove cleared rows
        self.grid = [
            row for i, row in enumerate(self.grid) if i not in set(rows)
        ]
        # Prepend empty rows at the top
        for _ in range(len(rows)):
            self.grid.insert(0, [None] * self.cols)

        return len(rows)

    # ── Ghost piece ─────────────────────────────────────────────────────

    def get_ghost_position(self, piece: Piece) -> list[tuple[int, int]]:
        """Return the cells of the piece dropped to its lowest valid row."""
        ghost_row = piece.row
        while self.is_valid_position(
            [(ghost_row + 1 + dr, piece.col + dc)
             for dr, dc in SHAPES[piece.name][piece.rotation]],
        ):
            ghost_row += 1
        offsets = SHAPES[piece.name][piece.rotation]
        return [(ghost_row + dr, piece.col + dc) for dr, dc in offsets]

    # ── Spawning ────────────────────────────────────────────────────────

    def spawn_piece(self) -> Piece | None:
        """Create a new random piece at the top-centre of the board.

        Returns None if the piece cannot be placed (game over).
        """
        name = random.choice(PIECE_NAMES)
        start_col = self.cols // 2 - 1
        piece = Piece(name, row=0, col=start_col)

        if not self.is_valid_position(piece.cells):
            return None  # game over

        return piece

    def clear(self) -> None:
        """Reset the board to empty."""
        self.grid = [[None] * self.cols for _ in range(self.rows)]

    # ── Debug ───────────────────────────────────────────────────────────

    def __repr__(self) -> str:
        return f"Board({self.rows}x{self.cols})"
