"""
Renderer — draws the board, pieces, UI panels, and overlays.

All drawing logic is isolated here so the game loop only calls render().
"""

from __future__ import annotations

import pygame

from src.core.board import Board
from src.core.game_state import GameState
from src.core.pieces import Piece
from src.ui.colors import COLORS
from src.utils.config import Config

# Font cache to avoid re-creating Font objects every frame
_FONTS: dict[str, pygame.font.Font] = {}


def _get_font(name: str, size: int) -> pygame.font.Font:
    key = f"{name}_{size}"
    if key not in _FONTS:
        _FONTS[key] = pygame.font.SysFont(name, size, bold=True)
    return _FONTS[key]


class Renderer:
    """Handles all drawing for the Tetris game."""

    def __init__(self, screen: pygame.Surface, config: Config) -> None:
        self.screen = screen
        self.cfg = config

        # Pre-calculate rects
        self.board_rect = pygame.Rect(
            config.BOARD_X_OFFSET,
            config.BOARD_Y_OFFSET,
            config.BOARD_PX_WIDTH,
            config.BOARD_PX_HEIGHT,
        )

    # ── Top-level render ──────────────────────────────────────────────────

    def render(
        self,
        board: Board,
        state: GameState,
        current_piece: Piece | None,
        ghost_cells: list[tuple[int, int]] | None,
        next_piece: Piece | None = None,
        held_piece: Piece | None = None,
        can_hold: bool = True,
    ) -> None:
        """Render the entire frame."""
        self.screen.fill(COLORS["BACKGROUND"])

        self._draw_board_background()
        self._draw_grid()
        self._draw_locked_cells(board)

        if ghost_cells and current_piece:
            self._draw_ghost(ghost_cells, current_piece.color)

        if current_piece:
            self._draw_piece(current_piece)

        self._draw_hold_panel(held_piece, can_hold)
        self._draw_panel(state, next_piece)

        if state.paused:
            self._draw_pause_overlay()
        elif state.game_over:
            self._draw_game_over_overlay(state.score)

        pygame.display.flip()

    # ── Board ─────────────────────────────────────────────────────────────

    def _draw_board_background(self) -> None:
        pygame.draw.rect(
            self.screen, COLORS["BOARD_BG"], self.board_rect,
        )
        pygame.draw.rect(
            self.screen, COLORS["BORDER"], self.board_rect, width=2,
        )

    def _draw_grid(self) -> None:
        for row in range(self.cfg.BOARD_ROWS):
            for col in range(self.cfg.BOARD_COLS):
                x = self.cfg.BOARD_X_OFFSET + col * self.cfg.CELL_SIZE
                y = self.cfg.BOARD_Y_OFFSET + row * self.cfg.CELL_SIZE
                rect = pygame.Rect(x, y, self.cfg.CELL_SIZE, self.cfg.CELL_SIZE)
                pygame.draw.rect(self.screen, COLORS["GRID_LINE"], rect, width=1)

    def _draw_locked_cells(self, board: Board) -> None:
        for row in range(board.rows):
            for col in range(board.cols):
                color = board.grid[row][col]
                if color is not None:
                    self._draw_cell(row, col, color)

    # ── Pieces ────────────────────────────────────────────────────────────

    def _draw_piece(self, piece: Piece) -> None:
        for row, col in piece.cells:
            self._draw_cell(row, col, piece.color)

    def _draw_ghost(self, cells: list[tuple[int, int]], color: pygame.Color) -> None:
        ghost_color = pygame.Color(color.r, color.g, color.b, self.cfg.GHOST_ALPHA)
        for row, col in cells:
            self._draw_cell(row, col, ghost_color, alpha=True)

    def _draw_cell(
        self,
        row: int,
        col: int,
        color: pygame.Color | tuple[int, int, int],
        alpha: bool = False,
    ) -> None:
        x = self.cfg.BOARD_X_OFFSET + col * self.cfg.CELL_SIZE
        y = self.cfg.BOARD_Y_OFFSET + row * self.cfg.CELL_SIZE
        rect = pygame.Rect(x + 1, y + 1, self.cfg.CELL_SIZE - 2, self.cfg.CELL_SIZE - 2)

        surface = pygame.Surface((self.cfg.CELL_SIZE - 2, self.cfg.CELL_SIZE - 2))
        if alpha:
            surface.set_alpha(self.cfg.GHOST_ALPHA)
        surface.fill(color)
        self.screen.blit(surface, (x + 1, y + 1))

        # Highlight / bevel effect
        lighter = self._lighten(color)
        pygame.draw.line(self.screen, lighter, rect.topleft, rect.topright, 2)
        pygame.draw.line(self.screen, lighter, rect.topleft, rect.bottomleft, 2)

    # ── Hold panel (left side) ────────────────────────────────────────────

    def _draw_hold_panel(self, held_piece: Piece | None, can_hold: bool) -> None:
        x = self.cfg.HOLD_PANEL_X
        y = self.cfg.HOLD_PANEL_Y

        # Panel background
        panel_rect = pygame.Rect(
            x, y, self.cfg.HOLD_PANEL_WIDTH,
            self.cfg.BOARD_PX_HEIGHT,
        )
        pygame.draw.rect(self.screen, COLORS["PANEL_BG"], panel_rect)
        pygame.draw.rect(self.screen, COLORS["BORDER"], panel_rect, width=2)

        # Hold label
        label_color = COLORS["TEXT_ACCENT"] if can_hold else COLORS["TEXT_DIM"]
        self._draw_text("HOLD", x + 15, y + 15, label_color, 20)

        # Held piece preview
        if held_piece:
            self._draw_piece_preview(held_piece, x + 20, y + 40)

    # ── Side panel ────────────────────────────────────────────────────────

    def _draw_panel(self, state: GameState, next_piece: Piece | None = None) -> None:
        x = self.cfg.PANEL_X
        y = self.cfg.PANEL_Y

        # Panel background
        panel_rect = pygame.Rect(
            x, y, self.cfg.PANEL_WIDTH,
            self.cfg.BOARD_PX_HEIGHT,
        )
        pygame.draw.rect(self.screen, COLORS["PANEL_BG"], panel_rect)
        pygame.draw.rect(self.screen, COLORS["BORDER"], panel_rect, width=2)

        # Next piece label
        self._draw_text("NEXT", x + 15, y + 15, COLORS["TEXT_ACCENT"], 20)

        # Next piece preview
        if next_piece:
            self._draw_piece_preview(next_piece, x + 20, y + 40)

        # Score
        self._draw_text("SCORE", x + 15, y + 200, COLORS["TEXT_ACCENT"], 18)
        self._draw_text(str(state.score), x + 15, y + 225, COLORS["TEXT_PRIMARY"], 28)

        # Level
        self._draw_text("LEVEL", x + 15, y + 280, COLORS["TEXT_ACCENT"], 18)
        self._draw_text(str(state.level), x + 15, y + 305, COLORS["TEXT_PRIMARY"], 28)

        # Lines
        self._draw_text("LINES", x + 15, y + 360, COLORS["TEXT_ACCENT"], 18)
        self._draw_text(str(state.lines), x + 15, y + 385, COLORS["TEXT_PRIMARY"], 28)

    def _draw_piece_preview(self, piece: Piece, origin_x: int, origin_y: int) -> None:
        """Draw a small preview of a piece in the side panel."""
        cells = piece.cells
        # Find bounding box to center the preview
        min_r = min(r for r, c in cells)
        max_r = max(r for r, c in cells)
        min_c = min(c for r, c in cells)
        max_c = max(c for r, c in cells)

        preview_cell = 20  # smaller cells for preview
        preview_w = (max_c - min_c + 1) * preview_cell
        preview_h = (max_r - min_r + 1) * preview_cell

        for row, col in cells:
            px = origin_x + (col - min_c) * preview_cell
            py = origin_y + (row - min_r) * preview_cell
            rect = pygame.Rect(px + 1, py + 1, preview_cell - 2, preview_cell - 2)
            pygame.draw.rect(self.screen, piece.color, rect)
            lighter = self._lighten(piece.color)
            pygame.draw.line(self.screen, lighter, rect.topleft, rect.topright, 2)
            pygame.draw.line(self.screen, lighter, rect.topleft, rect.bottomleft, 2)

    # ── Overlays ──────────────────────────────────────────────────────────

    def _draw_pause_overlay(self) -> None:
        overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        self.screen.blit(overlay, (0, 0))

        self._draw_text_centered(
            "PAUSED",
            self.cfg.WINDOW_WIDTH // 2,
            self.cfg.WINDOW_HEIGHT // 2 - 60,
            COLORS["TEXT_ACCENT"],
            48,
        )
        self._draw_text_centered(
            "Press ESC or P to resume",
            self.cfg.WINDOW_WIDTH // 2,
            self.cfg.WINDOW_HEIGHT // 2,
            COLORS["TEXT_PRIMARY"],
            18,
        )

        # Quit button
        btn_cx = self.cfg.WINDOW_WIDTH // 2
        btn_y = self.cfg.WINDOW_HEIGHT // 2 + 50
        btn_w, btn_h = 160, 40
        btn_rect = pygame.Rect(btn_cx - btn_w // 2, btn_y, btn_w, btn_h)
        pygame.draw.rect(self.screen, COLORS["BUTTON_DANGER"], btn_rect, border_radius=6)
        self._draw_text_centered(
            "QUIT",
            btn_cx,
            btn_y + btn_h // 2,
            COLORS["TEXT_PRIMARY"],
            22,
        )

    def _draw_game_over_overlay(self, score: int) -> None:
        overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        self._draw_text_centered(
            "GAME OVER",
            self.cfg.WINDOW_WIDTH // 2,
            self.cfg.WINDOW_HEIGHT // 2 - 40,
            COLORS["TEXT_GAME_OVER"],
            52,
        )
        self._draw_text_centered(
            f"Score: {score}",
            self.cfg.WINDOW_WIDTH // 2,
            self.cfg.WINDOW_HEIGHT // 2 + 10,
            COLORS["TEXT_PRIMARY"],
            28,
        )
        self._draw_text_centered(
            "Press R to restart or ESC to quit",
            self.cfg.WINDOW_WIDTH // 2,
            self.cfg.WINDOW_HEIGHT // 2 + 50,
            COLORS["TEXT_PRIMARY"],
            18,
        )

    # ── Text helpers ──────────────────────────────────────────────────────

    def _draw_text(
        self,
        text: str,
        x: int,
        y: int,
        color: pygame.Color,
        size: int,
    ) -> None:
        font = _get_font("monospace", size)
        surface = font.render(text, True, color)
        self.screen.blit(surface, (x, y))

    def _draw_text_centered(
        self,
        text: str,
        cx: int,
        cy: int,
        color: pygame.Color,
        size: int,
    ) -> None:
        font = _get_font("monospace", size)
        surface = font.render(text, True, color)
        rect = surface.get_rect(center=(cx, cy))
        self.screen.blit(surface, rect)

    # ── Utility ───────────────────────────────────────────────────────────

    @staticmethod
    def _lighten(
        color: pygame.Color | tuple[int, int, int],
        factor: float = 0.3,
    ) -> tuple[int, int, int]:
        r = min(255, int(color[0] + (255 - color[0]) * factor))
        g = min(255, int(color[1] + (255 - color[1]) * factor))
        b = min(255, int(color[2] + (255 - color[2]) * factor))
        return (r, g, b)
