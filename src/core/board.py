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
        """Check if a cell is within the board boundaries.

        Negative rows (above the visible playfield) are allowed so that
        piece shapes can extend above the visible area without being
        considered out of bounds.
        """
        return -self.rows <= row < self.rows and 0 <= col < self.cols

    def is_cell_empty(self, row: int, col: int) -> bool:
        """Check if a cell is unoccupied.

        Negative rows (above the board) are always treated as empty.
        Out-of-bounds bottom or columns are considered blocked.
        """
        if not self.is_in_bounds(row, col):
            return False
        if row < 0:
            return True   # above the board = empty space
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
        """Write the piece's cells into the grid permanently.

        Only writes cells that are within the actual grid area (row >= 0).
        Cells above the board (negative row) are silently dropped.
        """
        for row, col in piece.cells:
            if 0 <= row < self.rows and 0 <= col < self.cols:
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
        """Create a new random piece at the top of the board.

        Tries spawning at row 3 first (visible top). If that position is
        blocked by the stack, shifts up one row at a time into the buffer
        zone (rows 2, 1, 0, -1). If even row -1 is blocked, returns None
        (game over).

        Negative rows above the board are valid — the piece peeks in from
        the top without overlapping the stack.
        """
        name = random.choice(PIECE_NAMES)
        start_col = self.cols // 2 - 1

        for row in (3, 2, 1, 0, -1):
            piece = Piece(name, row=row, col=start_col)
            if self.is_valid_position(piece.cells):
                return piece

        return None  # game over

    def clear(self) -> None:
        """Reset the board to empty."""
        self.grid = [[None] * self.cols for _ in range(self.rows)]

    # ── Debug ───────────────────────────────────────────────────────────

    def __repr__(self) -> str:
        return f"Board({self.rows}x{self.cols})"
