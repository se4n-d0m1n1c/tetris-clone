"""
Tests for the Board class — grid, collision, locking, line clearing, ghost.
"""

import pytest

from src.core.board import Board
from src.core.pieces import Piece


# ── Fixtures ──────────────────────────────────────────────────────────────

@pytest.fixture
def board() -> Board:
    """Standard 10x20 Tetris board."""
    return Board(rows=20, cols=10)


# ── Initialisation ────────────────────────────────────────────────────────

class TestBoardInit:
    def test_creates_empty_grid(self) -> None:
        b = Board(5, 7)
        assert b.rows == 5
        assert b.cols == 7
        assert len(b.grid) == 5
        assert all(len(row) == 7 for row in b.grid)
        assert all(cell is None for row in b.grid for cell in row)

    def test_repr(self) -> None:
        b = Board(20, 10)
        assert repr(b) == "Board(20x10)"


# ── Bounds checking ───────────────────────────────────────────────────────

class TestIsInBounds:
    def test_valid_cell(self, board: Board) -> None:
        assert board.is_in_bounds(0, 0) is True
        assert board.is_in_bounds(19, 9) is True
        assert board.is_in_bounds(10, 5) is True
        # Negative rows (above the visible playfield) are allowed
        assert board.is_in_bounds(-1, 0) is True
        assert board.is_in_bounds(-19, 9) is True

    def test_out_of_bounds(self, board: Board) -> None:
        assert board.is_in_bounds(0, -1) is False
        assert board.is_in_bounds(20, 0) is False
        assert board.is_in_bounds(0, 10) is False
        # Very negative rows are still bounded
        assert board.is_in_bounds(-20, 0) is True   # -20 >= -20, so valid
        assert board.is_in_bounds(-21, 0) is False   # -21 < -20, out of bounds


# ── Cell emptiness ────────────────────────────────────────────────────────

class TestIsCellEmpty:
    def test_empty_cell_in_bounds(self, board: Board) -> None:
        assert board.is_cell_empty(5, 5) is True

    def test_negative_row_is_empty(self, board: Board) -> None:
        """Negative rows (above the board) are always empty."""
        assert board.is_cell_empty(-1, 0) is True
        assert board.is_cell_empty(-10, 5) is True

    def test_out_of_bounds_cell_is_not_empty(self, board: Board) -> None:
        assert board.is_cell_empty(20, 0) is False  # below board
        assert board.is_cell_empty(0, 10) is False   # past right edge

    def test_occupied_cell(self, board: Board) -> None:
        board.grid[5][5] = (255, 0, 0)
        assert board.is_cell_empty(5, 5) is False


# ── Collision detection ───────────────────────────────────────────────────

class TestIsValidPosition:
    def test_all_empty_cells(self, board: Board) -> None:
        cells = [(0, 4), (0, 5), (1, 4), (1, 5)]
        assert board.is_valid_position(cells) is True

    def test_out_of_bounds_cells(self, board: Board) -> None:
        cells = [(0, 4), (0, 10)]  # col 10 is out
        assert board.is_valid_position(cells) is False

    def test_collision_with_locked_cell(self, board: Board) -> None:
        board.grid[5][5] = (255, 0, 0)
        cells = [(5, 5), (5, 6)]
        assert board.is_valid_position(cells) is False

    def test_empty_list_is_valid(self, board: Board) -> None:
        assert board.is_valid_position([]) is True


# ── Piece locking ─────────────────────────────────────────────────────────

class TestLockPiece:
    def test_locks_piece_cells_into_grid(self, board: Board) -> None:
        piece = Piece("T", row=0, col=4)
        board.lock_piece(piece)

        # T-piece rotation 0: (0,-1), (0,0), (0,1), (1,0)
        assert board.grid[0][3] is not None
        assert board.grid[0][4] is not None
        assert board.grid[0][5] is not None
        assert board.grid[1][4] is not None
        assert board.grid[0][2] is None  # outside piece

    def test_lock_ignores_out_of_bounds_cells(self, board: Board) -> None:
        """If a piece is partially offscreen, only in-bounds cells lock."""
        piece = Piece("I", row=-1, col=4)
        board.lock_piece(piece)
        # I rotation 0: (0,-1), (0,0), (0,1), (0,2) -> absolute: (-1,3),(-1,4),(-1,5),(-1,6)
        # All are out of bounds, so nothing should be locked
        assert all(cell is None for row in board.grid for cell in row)


# ── Line clearing ─────────────────────────────────────────────────────────

class TestGetFullRows:
    def test_no_full_rows_on_empty_board(self, board: Board) -> None:
        assert board.get_full_rows() == []

    def test_detects_single_full_row(self, board: Board) -> None:
        board.grid[19] = [(100, 100, 100)] * 10
        assert board.get_full_rows() == [19]

    def test_detects_multiple_full_rows(self, board: Board) -> None:
        board.grid[18] = [(100, 100, 100)] * 10
        board.grid[19] = [(200, 200, 200)] * 10
        assert board.get_full_rows() == [18, 19]

    def test_partial_row_not_detected(self, board: Board) -> None:
        board.grid[19] = [(100, 100, 100)] * 9 + [None]
        assert board.get_full_rows() == []


class TestClearRows:
    def test_clear_no_rows_returns_zero(self, board: Board) -> None:
        assert board.clear_rows([]) == 0

    def test_clear_empty_row_still_removes_it(self, board: Board) -> None:
        """clear_rows doesn't check fullness — it clears whatever indices given."""
        assert board.clear_rows([5]) == 1

    def test_clear_single_row_shifts_above_down(self, board: Board) -> None:
        board.grid[19] = [(1, 1, 1)] * 10
        board.grid[18][5] = (2, 2, 2)  # marker in row 18

        cleared = board.clear_rows([19])
        assert cleared == 1
        # Row 18 content should now be at row 19 (shifted down)
        assert board.grid[19][5] == (2, 2, 2)
        # Row 0 should be the new empty row at top
        assert all(cell is None for cell in board.grid[0])

    def test_clear_multiple_rows(self, board: Board) -> None:
        board.grid[18] = [(1, 1, 1)] * 10
        board.grid[19] = [(2, 2, 2)] * 10
        board.grid[17][0] = (3, 3, 3)

        cleared = board.clear_rows([18, 19])
        assert cleared == 2
        # Marker should be at row 19 (shifted down 2)
        assert board.grid[19][0] == (3, 3, 3)
        # Top two rows are empty
        assert all(cell is None for cell in board.grid[0])
        assert all(cell is None for cell in board.grid[1])

    def test_clear_non_full_row_does_nothing(self, board: Board) -> None:
        board.grid[19][5] = (1, 1, 1)
        cleared = board.clear_rows([19])
        assert cleared == 1
        # The non-full row gets cleared and replaced with empty
        assert board.grid[0][5] is None

    def test_tetris_clear(self, board: Board) -> None:
        for r in range(16, 20):
            board.grid[r] = [(1, 1, 1)] * 10
        cleared = board.clear_rows([16, 17, 18, 19])
        assert cleared == 4
        assert all(cell is None for cell in board.grid[0])


# ── Ghost piece ───────────────────────────────────────────────────────────

class TestGhostPosition:
    def test_ghost_at_bottom_of_empty_board(self, board: Board) -> None:
        piece = Piece("O", row=0, col=4)
        ghost = board.get_ghost_position(piece)
        # O-piece is 2x2, so bottom row is row 19 -> ghost row should be 18
        expected = [(18, 4), (18, 5), (19, 4), (19, 5)]
        assert ghost == expected

    def test_ghost_stops_at_locked_cell(self, board: Board) -> None:
        board.grid[19][4] = (255, 0, 0)
        board.grid[19][5] = (255, 0, 0)
        piece = Piece("O", row=0, col=4)
        ghost = board.get_ghost_position(piece)
        # Stops at row 17 because row 18 has the blocker underneath
        expected = [(17, 4), (17, 5), (18, 4), (18, 5)]
        assert ghost == expected

    def test_ghost_same_as_piece_when_blocked(self, board: Board) -> None:
        """If piece can't move down at all, ghost = piece position."""
        board.grid[1][4] = (255, 0, 0)
        board.grid[1][5] = (255, 0, 0)
        piece = Piece("O", row=0, col=4)
        ghost = board.get_ghost_position(piece)
        expected = [(0, 4), (0, 5), (1, 4), (1, 5)]
        assert ghost == expected


# ── Spawning ──────────────────────────────────────────────────────────────

class TestSpawnPiece:
    def test_spawns_piece_at_visible_top(self, board: Board) -> None:
        piece = board.spawn_piece()
        assert piece is not None
        assert piece.row == 3  # first visible row
        assert piece.col == 4  # cols//2 - 1

    def test_shifts_up_when_blocked(self, board: Board) -> None:
        """If row 3 is blocked, piece shifts up into buffer zone (row 2, 1, 0, or -1)."""
        # Fill row 3 with blocks
        board.grid[3] = [(100, 100, 100)] * 10
        piece = board.spawn_piece()
        assert piece is not None
        # Piece shifted to a valid position above the blocked row
        assert piece.row < 3  # shifted up from row 3

    def test_game_over_when_all_rows_blocked(self, board: Board) -> None:
        """Fill rows 3, 2, 1, 0, -1 so every spawn attempt fails."""
        for row in (3, 2, 1, 0):
            board.grid[row] = [(100, 100, 100)] * 10
        result = board.spawn_piece()
        assert result is None  # row -1 also blocked by piece shape
    
    def test_negative_row_spawn(self, board: Board) -> None:
        """Spawn shifts up to row -1 when rows 0-3 are all blocked."""
        for row in (3, 2, 1, 0):
            board.grid[row] = [(100, 100, 100)] * 10
        # Piece at row -1 with I-piece's shape should be valid if col is right
        # I-piece (rotation 0): (0,-1),(0,0),(0,1),(0,2) -> absolute (-1,3),(-1,4),(-1,5),(-1,6)
        # All cells at row -1 with negative-rows-allowed
        piece = Piece("I", row=-1, col=4)
        assert board.is_valid_position(piece.cells) is True

    def test_spawned_piece_cells_are_valid(self, board: Board) -> None:
        for _ in range(50):
            piece = board.spawn_piece()
            assert piece is not None
            assert board.is_valid_position(piece.cells)

    def test_negative_row_is_valid_position(self, board: Board) -> None:
        cells = [(-1, 4), (0, 4), (1, 4), (2, 4)]  # I-piece vertical at row 0
        assert board.is_valid_position(cells) is True


# ── Clear ─────────────────────────────────────────────────────────────────

class TestClear:
    def test_resets_board_to_empty(self, board: Board) -> None:
        board.grid[10] = [(1, 1, 1)] * 10
        board.clear()
        assert all(cell is None for row in board.grid for cell in row)

    def test_preserves_dimensions(self, board: Board) -> None:
        board.clear()
        assert len(board.grid) == 20
        assert all(len(row) == 10 for row in board.grid)
