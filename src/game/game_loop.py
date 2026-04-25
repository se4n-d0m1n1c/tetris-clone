"""
Game loop — orchestrates the main game update/render cycle.

Handles timing, gravity, piece locking, line clears, and state transitions.
Input events are forwarded to the InputHandler.
"""

from __future__ import annotations

import pygame

from src.core.board import Board
from src.core.game_state import GameState
from src.core.pieces import Piece
from src.game.input_handler import InputHandler, InputAction
from src.ui.renderer import Renderer
from src.utils.config import Config


class GameLoop:
    """The central game loop — owns Board, GameState, Renderer, InputHandler."""

    def __init__(
        self,
        screen: pygame.Surface,
        clock: pygame.time.Clock,
        config: Config,
    ) -> None:
        self.screen = screen
        self.clock = clock
        self.cfg = config
        self.renderer = Renderer(screen, config)
        self.input_handler = InputHandler()

        # Game objects
        self.board = Board(config.BOARD_ROWS, config.BOARD_COLS)
        self.state = GameState(config)
        self.current_piece: Piece | None = None
        self.next_piece: Piece | None = None
        self.held_piece: Piece | None = None
        self._can_hold: bool = True

        # Timing
        self._drop_timer: float = 0.0
        self._lock_timer: float = 0.0
        self._is_locking: bool = False

        # Start — pre-generate next piece before first spawn
        self.next_piece = self.board.spawn_piece()
        self._spawn_next()

    # ── Public API ────────────────────────────────────────────────────────

    def run(self) -> None:
        """Main loop — call once to run the game until the user quits."""
        while True:
            dt = self.clock.tick(self.cfg.FPS) / 1000.0  # seconds

            events = pygame.event.get()
            actions = self.input_handler.get_actions(events, dt)

            # Quit is always handled
            if InputAction.QUIT in actions:
                break

            if InputAction.RESTART in actions:
                self._restart()

            if InputAction.PAUSE in actions:
                if not self.state.game_over:
                    self.state.toggle_pause()
                else:
                    # On game-over screen, ESC / P means quit
                    break

            # Handle mouse clicks on the pause overlay quit button
            if self.state.paused:
                for event in events:
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        if self._is_quit_button_click(event.pos, self.cfg):
                            return  # quit the game

            if not self.state.paused and not self.state.game_over:
                self._handle_actions(actions)
                self._update(dt)

            self._render()

        pygame.quit()

    # ── Update logic ──────────────────────────────────────────────────────

    def _update(self, dt: float) -> None:
        """Advance the game simulation by *dt* seconds."""
        if self.current_piece is None:
            return

        # Gravity — drop the piece at the current speed
        self._drop_timer += dt * 1000  # convert to ms
        if self._drop_timer >= self.state.drop_interval:
            self._drop_timer = 0.0
            self._move_piece(1, 0)

        # Lock delay — if piece is resting, start / extend the lock timer
        if self._is_locking:
            self._lock_timer += dt * 1000
            if self._lock_timer >= self.cfg.LOCK_DELAY:
                self._lock_and_spawn()
        else:
            self._lock_timer = 0.0

    def _handle_actions(self, actions: list[str]) -> None:
        """Process all input actions for this frame."""
        if self.current_piece is None:
            return

        for action in actions:
            if action == InputAction.MOVE_LEFT:
                self._move_piece(0, -1)
            elif action == InputAction.MOVE_RIGHT:
                self._move_piece(0, 1)
            elif action == InputAction.SOFT_DROP:
                if self._move_piece(1, 0):
                    self._drop_timer = 0.0
                    self.state.score += 1  # soft-drop bonus
            elif action == InputAction.HARD_DROP:
                self._hard_drop()
            elif action == InputAction.ROTATE_CW:
                self._rotate(1)
            elif action == InputAction.ROTATE_CCW:
                self._rotate(-1)
            elif action == InputAction.HOLD:
                self._hold_piece()

    # ── Movement helpers ──────────────────────────────────────────────────

    def _move_piece(self, dr: int, dc: int) -> bool:
        """Attempt to move the current piece. Returns True if it moved."""
        if self.current_piece is None:
            return False
        new_cells = self.current_piece.get_moved_cells(dr, dc)
        if self.board.is_valid_position(new_cells):
            self.current_piece.row += dr
            self.current_piece.col += dc
            self._check_resting()
            return True
        # If trying to move down and failing, piece is resting
        if dr == 1:
            self._is_locking = True
        return False

    def _hard_drop(self) -> None:
        """Drop the piece instantly to the lowest valid row."""
        if self.current_piece is None:
            return
        while self.board.is_valid_position(
            self.current_piece.get_moved_cells(1, 0),
        ):
            self.current_piece.row += 1
            self.state.score += 2  # hard-drop bonus
        self._lock_and_spawn()

    def _rotate(self, direction: int) -> None:
        """Attempt SRS rotation with wall kicks."""
        if self.current_piece is None:
            return
        kicks = self.current_piece.get_wall_kicks(direction)
        new_rot = (self.current_piece.rotation + direction) % 4

        for kick_r, kick_c in kicks:
            # Build cells at the new rotation + kick offset
            test_cells = self.current_piece.get_rotated_cells(direction)
            test_cells = [(r + kick_r, c + kick_c) for r, c in test_cells]

            if self.board.is_valid_position(test_cells):
                self.current_piece.rotation = new_rot
                self.current_piece.row += kick_r
                self.current_piece.col += kick_c
                self._check_resting()
                return

    def _check_resting(self) -> None:
        """Update locking state based on whether the piece can fall."""
        if self.current_piece is None:
            return
        if not self.board.is_valid_position(
            self.current_piece.get_moved_cells(1, 0),
        ):
            self._is_locking = True
        else:
            self._is_locking = False
            self._lock_timer = 0.0

    # ── Locking & spawning ───────────────────────────────────────────────

    def _lock_and_spawn(self) -> None:
        """Lock the current piece into the board, clear lines, spawn next."""
        if self.current_piece is None:
            return

        self.board.lock_piece(self.current_piece)

        # Clear lines
        full_rows = self.board.get_full_rows()
        if full_rows:
            cleared = self.board.clear_rows(full_rows)
            self.state.add_score(cleared)

        self._spawn_next()

    def _spawn_next(self) -> None:
        """Promote next_piece to current (revalidating position), then generate a new next_piece."""
        # Re-validate the piece's spawn position based on current board state.
        # The previously generated next_piece may be blocked now after the last lock.
        centre = self.cfg.BOARD_COLS // 2 - 1
        name = self.next_piece.name if self.next_piece else None

        if name is None:
            self.current_piece = None
            self.state.end_game()
            return

        # Find the first valid spawn row (from row 3 down to -1)
        candidate = None
        for row in (3, 2, 1, 0, -1):
            candidate = Piece(name, row, centre)
            if self.board.is_valid_position(candidate.cells):
                self.current_piece = candidate
                break
        else:
            # No valid position for this piece type = game over
            self.current_piece = None
            self.state.end_game()
            return

        # Generate a fresh next piece
        self.next_piece = self.board.spawn_piece()

        self._drop_timer = 0.0
        self._lock_timer = 0.0
        self._is_locking = False
        self._can_hold = True

    # ── Hold ───────────────────────────────────────────────────────────────

    def _hold_piece(self) -> None:
        """Swap the current piece with the held piece (or store it)."""
        if self.current_piece is None or not self._can_hold:
            return

        prev_name = self.current_piece.name
        self._can_hold = False

        if self.held_piece is not None:
            # Swap: current goes to hold, held becomes current
            hold_name = self.held_piece.name
            self.held_piece = Piece(prev_name, 0, 3)
            # Re-spawn the held piece at centre, uses spawn logic (row 3, then shift up)
            centre = self.cfg.BOARD_COLS // 2 - 1
            self.current_piece = Piece(hold_name, 3, centre)
            if not self.board.is_valid_position(self.current_piece.cells):
                # Try shifting up into buffer zone
                for row in (2, 1, 0, -1):
                    self.current_piece = Piece(hold_name, row, centre)
                    if self.board.is_valid_position(self.current_piece.cells):
                        break
                else:
                    self.state.end_game()
        else:
            # First hold: store current, spawn next
            self.held_piece = Piece(prev_name, 0, 3)
            # Promote next_piece, but ensure it's valid at spawn position
            centre = self.cfg.BOARD_COLS // 2 - 1
            self.current_piece = Piece(self.next_piece.name, 3, centre)
            if not self.board.is_valid_position(self.current_piece.cells):
                # Try shifting up into buffer zone
                for row in (2, 1, 0, -1):
                    self.current_piece = Piece(self.next_piece.name, row, centre)
                    if self.board.is_valid_position(self.current_piece.cells):
                        break
                else:
                    self.state.end_game()
            self.next_piece = self.board.spawn_piece()

        self._drop_timer = 0.0
        self._lock_timer = 0.0
        self._is_locking = False

    # ── Ghost piece ───────────────────────────────────────────────────────

    @staticmethod
    def _is_quit_button_click(pos: tuple[int, int], cfg: Config) -> bool:
        """Check if a click is inside the pause overlay quit button."""
        btn_cx = cfg.WINDOW_WIDTH // 2
        btn_y = cfg.WINDOW_HEIGHT // 2 + 50
        btn_w, btn_h = 160, 40
        rect = pygame.Rect(btn_cx - btn_w // 2, btn_y, btn_w, btn_h)
        return rect.collidepoint(pos)

    def _get_ghost_cells(self) -> list[tuple[int, int]] | None:
        """Return the ghost piece cells for the current piece, or None."""
        if self.current_piece is None or self.state.game_over:
            return None
        return self.board.get_ghost_position(self.current_piece)

    # ── Render ────────────────────────────────────────────────────────────

    def _render(self) -> None:
        ghost = self._get_ghost_cells()
        self.renderer.render(
            self.board, self.state, self.current_piece, ghost,
            self.next_piece, self.held_piece, self._can_hold,
        )

    # ── Restart ───────────────────────────────────────────────────────────

    def _restart(self) -> None:
        self.board.clear()
        self.state.reset()
        self.current_piece = None
        self.held_piece = None
        self._can_hold = True
        self.next_piece = self.board.spawn_piece()
        self._spawn_next()
