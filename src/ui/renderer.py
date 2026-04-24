"""
Renderer — draws the board, pieces, UI panels, and overlays.

All drawing logic is isolated here so the game loop only calls render().
CYBER BLUE theme — electric blue / cyan / deep indigo on dark navy.
"""

from __future__ import annotations

import math
import os

import pygame

from src.core.board import Board
from src.core.game_state import GameState
from src.core.pieces import Piece
from src.ui.colors import COLORS
from src.utils.config import Config

# Font cache
_FONTS: dict[str, pygame.font.Font] = {}

_FONT_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "assets", "fonts")
_PRESS_START_PATH = os.path.join(_FONT_DIR, "PressStart2P-Regular.ttf")


def _get_font(name: str, size: int) -> pygame.font.Font:
    key = f"{name}_{size}"
    if key not in _FONTS:
        if name == "press_start" and os.path.exists(_PRESS_START_PATH):
            _FONTS[key] = pygame.font.Font(_PRESS_START_PATH, size)
        elif name == "led" and os.path.exists(_PRESS_START_PATH):
            _FONTS[key] = pygame.font.Font(_PRESS_START_PATH, int(size * 0.85))
        else:
            _FONTS[key] = pygame.font.SysFont("monospace", size, bold=True)
    return _FONTS[key]


class Renderer:
    """Handles all drawing for the Tetris game — cyber blue aesthetic."""

    def __init__(self, screen: pygame.Surface, config: Config) -> None:
        self.screen = screen
        self.cfg = config
        self.CELL = config.CELL_SIZE

        self.board_r = pygame.Rect(
            config.BOARD_X_OFFSET,
            config.BOARD_Y_OFFSET,
            config.BOARD_PX_WIDTH,
            config.BOARD_PX_HEIGHT,
        )

        self._frame_count = 0

        # Pre-compute grid line positions
        self._grid_lines: list[tuple[int, int, int, int]] = []
        for row in range(1, config.BOARD_ROWS):
            y = config.BOARD_Y_OFFSET + row * self.CELL
            self._grid_lines.append(
                (config.BOARD_X_OFFSET, y, config.BOARD_X_OFFSET + config.BOARD_PX_WIDTH, y)
            )
        for col in range(1, config.BOARD_COLS):
            x = config.BOARD_X_OFFSET + col * self.CELL
            self._grid_lines.append(
                (x, config.BOARD_Y_OFFSET, x, config.BOARD_Y_OFFSET + config.BOARD_PX_HEIGHT)
            )

        self._scanline_surf: pygame.Surface | None = None

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
        self._frame_count += 1

        self._draw_background()
        self._draw_board_bg(state)
        self._draw_grid()

        if ghost_cells and current_piece:
            self._draw_ghost(ghost_cells, current_piece.color)

        self._draw_locked(board)

        if current_piece:
            self._draw_piece(current_piece)

        self._draw_hold_panel(held_piece, can_hold)
        self._draw_panel(state, next_piece)

        self._draw_scanlines()
        self._draw_title_bar()

        if state.paused:
            self._draw_pause_overlay()
        elif state.game_over:
            self._draw_game_over_overlay(state.score)

        pygame.display.flip()

    # ── Background ────────────────────────────────────────────────────────

    def _draw_background(self) -> None:
        """Deep navy to indigo gradient."""
        w, h = self.screen.get_size()
        for y in range(h):
            t = y / h
            r = int(8 + 6 * t)
            g = int(8 + 10 * t)
            b = int(18 + 28 * t)
            pygame.draw.line(self.screen, (r, g, b), (0, y), (w - 1, y))

        # Subtle horizontal scan-tape lines
        for y in range(0, h, 6):
            alpha = 6 + 4 * (y % 12 == 0)
            c = (15, 20, 35, alpha)
            pygame.draw.line(self.screen, (c[0], c[1], c[2]), (0, y), (w, y), 1)

    def _draw_scanlines(self) -> None:
        """CRT scanline overlay — very faint."""
        w, h = self.screen.get_size()
        if self._scanline_surf is None or self._scanline_surf.get_size() != (w, h):
            self._scanline_surf = pygame.Surface((w, h), pygame.SRCALPHA)
            for y in range(0, h, 3):
                pygame.draw.line(self._scanline_surf, (0, 0, 0, 15),
                                 (0, y), (w, y), 1)
        self.screen.blit(self._scanline_surf, (0, 0))

    # ── Board ─────────────────────────────────────────────────────────────

    def _draw_board_bg(self, state: GameState) -> None:
        """Board background with pulsing electric-blue neon border."""
        rect = self.board_r
        pulse = 0.5 + 0.5 * math.sin(self._frame_count * 0.025)

        if state.game_over:
            bg = COLORS["BOARD_BG_GAME_OVER"]
            r_glow = int(100 + 80 * pulse)
            border_glow = pygame.Color(r_glow, 10, 20)
        else:
            bg = COLORS["BOARD_BG"]
            # Electric blue pulsing border — deeper and with a cyan outer edge
            base_b = int(160 + 80 * pulse)
            base_g = int(60 + 40 * pulse)
            border_glow = pygame.Color(20, base_g, min(255, base_b))

        # Board background
        pygame.draw.rect(self.screen, bg, rect)

        # Multi-ring outer glow
        glow_r = rect.inflate(10, 10)
        for i in range(5, 0, -1):
            alpha = max(0, 55 - i * 10)
            glow_layer = pygame.Surface(glow_r.size, pygame.SRCALPHA)
            pygame.draw.rect(glow_layer, (*border_glow[:3], alpha),
                             glow_layer.get_rect(), width=i + 1)
            self.screen.blit(glow_layer, (glow_r.x, glow_r.y))

        # Main border — thick
        pygame.draw.rect(self.screen, border_glow, rect, width=3)

        # Inner bright highlight
        inner_r = rect.inflate(-4, -4)
        highlight = pygame.Color(
            min(255, border_glow[0] + 50),
            min(255, border_glow[1] + 50),
            min(255, border_glow[2] + 30),
        )
        pygame.draw.rect(self.screen, highlight, inner_r, width=1)

        # Corner brackets (decorative)
        bracket_len = 12
        b_x, b_y, b_w, b_h = rect
        bracket_color = COLORS["PANEL_ACCENT"]
        # Top-left
        pygame.draw.line(self.screen, bracket_color, (b_x, b_y), (b_x + bracket_len, b_y), 2)
        pygame.draw.line(self.screen, bracket_color, (b_x, b_y), (b_x, b_y + bracket_len), 2)
        # Top-right
        pygame.draw.line(self.screen, bracket_color, (b_x + b_w - bracket_len, b_y), (b_x + b_w, b_y), 2)
        pygame.draw.line(self.screen, bracket_color, (b_x + b_w - 1, b_y), (b_x + b_w - 1, b_y + bracket_len), 2)
        # Bottom-left
        pygame.draw.line(self.screen, bracket_color, (b_x, b_y + b_h - 1), (b_x + bracket_len, b_y + b_h - 1), 2)
        pygame.draw.line(self.screen, bracket_color, (b_x, b_y + b_h - bracket_len), (b_x, b_y + b_h - 1), 2)
        # Bottom-right
        pygame.draw.line(self.screen, bracket_color, (b_x + b_w - bracket_len, b_y + b_h - 1), (b_x + b_w, b_y + b_h - 1), 2)
        pygame.draw.line(self.screen, bracket_color, (b_x + b_w - 1, b_y + b_h - bracket_len), (b_x + b_w - 1, b_y + b_h - 1), 2)

    def _draw_grid(self) -> None:
        """Draw faint blue grid lines."""
        for x1, y1, x2, y2 in self._grid_lines:
            pygame.draw.line(self.screen, COLORS["GRID_LINE"], (x1, y1), (x2, y2), 1)

        # Central vertical axis line (subtle)
        cx = self.cfg.BOARD_X_OFFSET + self.cfg.BOARD_PX_WIDTH // 2
        cy = self.cfg.BOARD_Y_OFFSET
        axis_color = (25, 30, 55)
        pygame.draw.line(self.screen, axis_color,
                         (cx, cy), (cx, cy + self.cfg.BOARD_PX_HEIGHT), 1)

    # ── Cells ─────────────────────────────────────────────────────────────

    def _draw_cell(self, row: int, col: int, color: pygame.Color,
                   alpha: int = 255, glow: bool = True) -> None:
        """Draw a single cell with glow and 3D bevel."""
        x = self.cfg.BOARD_X_OFFSET + col * self.CELL
        y = self.cfg.BOARD_Y_OFFSET + row * self.CELL
        cell_r = pygame.Rect(x + 1, y + 1, self.CELL - 2, self.CELL - 2)

        # Outer glow
        if glow and alpha > 128:
            glow_surf = pygame.Surface((self.CELL + 6, self.CELL + 6), pygame.SRCALPHA)
            glow_color = (*color[:3], 35)
            center = (self.CELL // 2 + 3, self.CELL // 2 + 3)
            pygame.draw.circle(glow_surf, glow_color, center, self.CELL // 2 + 2)
            self.screen.blit(glow_surf, (x - 3, y - 3))

        # Cell body
        body = pygame.Surface(cell_r.size)
        body_color = color[:3]
        if alpha < 255:
            body.set_alpha(alpha)
        body.fill(body_color)
        self.screen.blit(body, cell_r.topleft)

        # 3D bevel — bright top-left
        lighter = self._lighten(color, 0.35)
        if alpha < 255:
            lighter = tuple(min(255, int(c * alpha // 255 + 30)) for c in lighter)
        pygame.draw.line(self.screen, lighter, cell_r.topleft, cell_r.topright, 2)
        pygame.draw.line(self.screen, lighter, cell_r.topleft, cell_r.bottomleft, 2)

        # Dark bottom-right shadow
        darker = self._darken(color, 0.3)
        pygame.draw.line(self.screen, darker, cell_r.topright, cell_r.bottomright, 2)
        pygame.draw.line(self.screen, darker, cell_r.bottomleft, cell_r.bottomright, 2)

    @staticmethod
    def _lighten(color, factor: float = 0.3):
        r = min(255, int(color[0] + (255 - color[0]) * factor))
        g = min(255, int(color[1] + (255 - color[1]) * factor))
        b = min(255, int(color[2] + (255 - color[2]) * factor))
        return r, g, b

    @staticmethod
    def _darken(color, factor: float = 0.3):
        r = int(color[0] * (1 - factor))
        g = int(color[1] * (1 - factor))
        b = int(color[2] * (1 - factor))
        return r, g, b

    # ── Piece rendering ───────────────────────────────────────────────────

    def _draw_piece(self, piece: Piece) -> None:
        for row, col in piece.cells:
            if row < 0:
                self._draw_cell(row, col, piece.color, alpha=100, glow=False)
            else:
                self._draw_cell(row, col, piece.color)

    def _draw_locked(self, board: Board) -> None:
        for row in range(board.rows):
            for col in range(board.cols):
                color = board.grid[row][col]
                if color is not None:
                    self._draw_cell(row, col, color)

    def _draw_ghost(self, cells: list[tuple[int, int]], color: pygame.Color) -> None:
        """Faint ghost — dashed outline feel."""
        ghost_color = pygame.Color(color.r, color.g, color.b, 50)
        ox = self.cfg.BOARD_X_OFFSET
        oy = self.cfg.BOARD_Y_OFFSET
        for row, col in cells:
            if row < 0:
                continue
            x = ox + col * self.CELL
            y = oy + row * self.CELL
            rect = pygame.Rect(x + 1, y + 1, self.CELL - 2, self.CELL - 2)
            # Corners only for ghost (more elegant)
            l = 6
            pygame.draw.line(self.screen, ghost_color, rect.topleft, (rect.x + l, rect.y), 1)
            pygame.draw.line(self.screen, ghost_color, rect.topleft, (rect.x, rect.y + l), 1)
            pygame.draw.line(self.screen, ghost_color, rect.topright, (rect.x + rect.w - l, rect.y), 1)
            pygame.draw.line(self.screen, ghost_color, rect.topright, (rect.x + rect.w, rect.y + l), 1)
            pygame.draw.line(self.screen, ghost_color, rect.bottomleft, (rect.x + l, rect.y + rect.h), 1)
            pygame.draw.line(self.screen, ghost_color, rect.bottomleft, (rect.x, rect.y + rect.h - l), 1)
            pygame.draw.line(self.screen, ghost_color, rect.bottomright, (rect.x + rect.w - l, rect.y + rect.h), 1)
            pygame.draw.line(self.screen, ghost_color, rect.bottomright, (rect.x + rect.w, rect.y + rect.h - l), 1)

    # ── Title bar ─────────────────────────────────────────────────────────

    def _draw_title_bar(self) -> None:
        """Retro game title at the very top with cyan glow."""
        cx = self.cfg.WINDOW_WIDTH // 2

        cylon_effect = 0.5 + 0.5 * math.sin(self._frame_count * 0.03)
        glow_r = int(100 + 100 * cylon_effect)

        title = "NEON GRID"
        subtitle = "TETRIS"

        # Cyan glow behind title
        glow_color = pygame.Color(0, glow_r, min(255, glow_r + 100), 80)
        for dx, dy in [(3, 0), (-3, 0), (0, 3), (0, -3), (2, 2), (-2, -2)]:
            self._draw_text_centered(title, cx + dx, 12 + dy, glow_color, 14)

        self._draw_text_centered(title, cx, 12, COLORS["TEXT_ACCENT"], 14)
        self._draw_text_centered(subtitle, cx, 32, COLORS["PANEL_ACCENT"], 10)

    # ── Hold panel (left side) ────────────────────────────────────────────

    def _draw_hold_panel(self, held_piece: Piece | None, can_hold: bool) -> None:
        x = self.cfg.HOLD_PANEL_X
        y = self.cfg.HOLD_PANEL_Y

        panel_r = pygame.Rect(x, y, self.cfg.HOLD_PANEL_WIDTH, self.cfg.BOARD_PX_HEIGHT)

        # Panel background
        pygame.draw.rect(self.screen, COLORS["PANEL_BG"], panel_r)

        # Glow behind panel
        glow_surf = pygame.Surface(panel_r.size, pygame.SRCALPHA)
        glow_color = (*COLORS["BOARD_GLOW"][:3], 15)
        pygame.draw.rect(glow_surf, glow_color, glow_surf.get_rect(), width=4)
        self.screen.blit(glow_surf, panel_r.topleft)

        # Border
        border_color = COLORS["BOARD_GLOW"]
        pygame.draw.rect(self.screen, border_color, panel_r, width=2)

        # Top accent line
        pygame.draw.line(self.screen, COLORS["PANEL_ACCENT"],
                         (x + 15, y + 5), (x + self.cfg.HOLD_PANEL_WIDTH - 15, y + 5), 2)

        # Label
        label_col = COLORS["TEXT_ACCENT"] if can_hold else COLORS["TEXT_DIM"]
        self._draw_text("HOLD", x + 12, y + 18, label_col, 12)

        # Preview frame
        preview_border = pygame.Rect(x + 10, y + 50,
                                     self.cfg.HOLD_PANEL_WIDTH - 20, 80)
        pygame.draw.rect(self.screen, (15, 15, 30), preview_border)
        pygame.draw.rect(self.screen, (30, 40, 70), preview_border, width=1)

        if held_piece:
            self._draw_piece_preview(held_piece, x + 15, y + 60, dimmed=not can_hold)

        # Corner brackets
        brk = 6
        bc = COLORS["PANEL_ACCENT"]
        pygame.draw.line(self.screen, bc, (x + 8, y + 8), (x + 8 + brk, y + 8), 1)
        pygame.draw.line(self.screen, bc, (x + 8, y + 8), (x + 8, y + 8 + brk), 1)

    # ── Side panel (right side) ──────────────────────────────────────────

    def _draw_panel(self, state: GameState, next_piece: Piece | None = None) -> None:
        x = self.cfg.PANEL_X
        y = self.cfg.PANEL_Y

        panel_r = pygame.Rect(x, y, self.cfg.PANEL_WIDTH, self.cfg.BOARD_PX_HEIGHT)

        pygame.draw.rect(self.screen, COLORS["PANEL_BG"], panel_r)

        glow_surf = pygame.Surface(panel_r.size, pygame.SRCALPHA)
        glow_color = (*COLORS["BOARD_GLOW"][:3], 15)
        pygame.draw.rect(glow_surf, glow_color, glow_surf.get_rect(), width=4)
        self.screen.blit(glow_surf, panel_r.topleft)

        border_color = COLORS["BOARD_GLOW"]
        pygame.draw.rect(self.screen, border_color, panel_r, width=2)

        pygame.draw.line(self.screen, COLORS["PANEL_ACCENT"],
                         (x + 15, y + 5), (x + self.cfg.PANEL_WIDTH - 15, y + 5), 2)

        # NEXT label
        self._draw_text("NEXT", x + 12, y + 18, COLORS["TEXT_ACCENT"], 12)

        # Preview frame
        preview_border = pygame.Rect(x + 10, y + 50,
                                     self.cfg.PANEL_WIDTH - 20, 80)
        pygame.draw.rect(self.screen, (15, 15, 30), preview_border)
        pygame.draw.rect(self.screen, (30, 40, 70), preview_border, width=1)

        if next_piece:
            self._draw_piece_preview(next_piece, x + 15, y + 60)

        # Corners
        brk = 6
        bc = COLORS["PANEL_ACCENT"]
        pygame.draw.line(self.screen, bc, (x + 8, y + 8), (x + 8 + brk, y + 8), 1)
        pygame.draw.line(self.screen, bc, (x + 8, y + 8), (x + 8, y + 8 + brk), 1)

        # Separator — horizontal line with glowing dot
        sep_y = y + 145
        pygame.draw.line(self.screen, (30, 40, 70),
                         (x + 10, sep_y), (x + self.cfg.PANEL_WIDTH - 10, sep_y), 1)
        # Glowing dot in center
        dot_cx = x + self.cfg.PANEL_WIDTH // 2
        dot_pulse = 0.6 + 0.4 * math.sin(self._frame_count * 0.04)
        dot_alpha = int(100 + 155 * dot_pulse)
        dot_color = pygame.Color(*COLORS["PANEL_ACCENT"][:3], dot_alpha)
        pygame.draw.circle(self.screen, dot_color, (dot_cx, sep_y), 3)

        # Stats
        stats_start = sep_y + 20

        self._draw_led_display("SCORE", str(state.score),
                                x + 12, stats_start, COLORS["PANEL_ACCENT"])
        level_y = stats_start + 48
        self._draw_led_display("LEVEL", str(state.level),
                               x + 12, level_y, COLORS["TEXT_ACCENT"])
        lines_y = level_y + 48
        self._draw_led_display("LINES", str(state.lines),
                               x + 12, lines_y, COLORS["TEXT_ACCENT"])

    def _draw_led_display(self, label: str, value: str, x: int, y: int,
                          value_color: pygame.Color) -> None:
        """Draw a compact LED-style label+value pair."""
        self._draw_text(label, x, y, COLORS["TEXT_DIM"], 9)

        # Dark LED background
        surf = _get_font("led", 18)
        val_surf = surf.render(value, True, value_color)
        val_rect = val_surf.get_rect(topleft=(x, y + 14))
        bg_rect = val_rect.inflate(8, 4)
        pygame.draw.rect(self.screen, (12, 12, 25), bg_rect)
        pygame.draw.rect(self.screen, (30, 35, 65), bg_rect, width=1)

        self.screen.blit(val_surf, val_rect.topleft)

    def _draw_piece_preview(self, piece: Piece, origin_x: int, origin_y: int,
                            dimmed: bool = False) -> None:
        """Draw a small preview of a piece."""
        cells = piece.cells
        min_r = min(r for r, c in cells)
        max_r = max(r for r, c in cells)
        min_c = min(c for r, c in cells)
        max_c = max(c for r, c in cells)

        preview_cell = 18
        for row, col in cells:
            px = origin_x + (col - min_c) * preview_cell
            py = origin_y + (row - min_r) * preview_cell
            rect = pygame.Rect(px + 1, py + 1, preview_cell - 2, preview_cell - 2)
            color = piece.color
            if dimmed:
                color = tuple(c // 3 for c in color)

            pygame.draw.rect(self.screen, color[:3], rect)

            lighter = self._lighten(color, 0.3)
            pygame.draw.line(self.screen, lighter, rect.topleft, rect.topright, 2)
            pygame.draw.line(self.screen, lighter, rect.topleft, rect.bottomleft, 1)

    # ── Overlays ──────────────────────────────────────────────────────────

    def _draw_pause_overlay(self) -> None:
        """Dark overlay with pulsing PAUSED dialog."""
        overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        self.screen.blit(overlay, (0, 0))

        pulse = 0.7 + 0.3 * math.sin(self._frame_count * 0.04)
        alpha = int(180 + 75 * pulse)
        pulsed = pygame.Color(*COLORS["TEXT_ACCENT"][:3], alpha)

        cx = self.cfg.WINDOW_WIDTH // 2
        cy = self.cfg.WINDOW_HEIGHT // 2

        box_w, box_h = 280, 170
        box_r = pygame.Rect(cx - box_w // 2, cy - box_h // 2 - 10, box_w, box_h)

        # Box background with border
        pygame.draw.rect(self.screen, (8, 8, 20), box_r)
        pygame.draw.rect(self.screen, COLORS["BOARD_GLOW"], box_r, width=2)

        # Inner highlight
        inner_box = box_r.inflate(-4, -4)
        pygame.draw.rect(self.screen, (20, 25, 55), inner_box, width=1)

        self._draw_text_centered("PAUSED", cx, cy - 30, pulsed, 28)
        self._draw_text_centered("Press ESC or P to resume", cx, cy + 10,
                                 COLORS["TEXT_PRIMARY"], 11)

        # Quit button
        btn_cx = cx
        btn_y = cy + 40
        btn_w, btn_h = 140, 32
        btn_rect = pygame.Rect(btn_cx - btn_w // 2, btn_y, btn_w, btn_h)
        pygame.draw.rect(self.screen, COLORS["BUTTON_DANGER"], btn_rect, border_radius=4)
        pygame.draw.rect(self.screen, (200, 30, 60), btn_rect, width=1, border_radius=4)
        self._draw_text_centered("QUIT", btn_cx, btn_y + btn_h // 2,
                                 COLORS["TEXT_PRIMARY"], 12)

        # Corner brackets
        brk = 8
        bc = COLORS["PANEL_ACCENT"]
        pygame.draw.line(self.screen, bc, (box_r.x + 6, box_r.y + 6), (box_r.x + 6 + brk, box_r.y + 6), 1)
        pygame.draw.line(self.screen, bc, (box_r.x + 6, box_r.y + 6), (box_r.x + 6, box_r.y + 6 + brk), 1)
        pygame.draw.line(self.screen, bc, (box_r.x + box_r.w - 6 - brk, box_r.y + 6), (box_r.x + box_r.w - 6, box_r.y + 6), 1)
        pygame.draw.line(self.screen, bc, (box_r.x + box_r.w - 6, box_r.y + 6), (box_r.x + box_r.w - 6, box_r.y + 6 + brk), 1)

    def _draw_game_over_overlay(self, score: int) -> None:
        """Dark overlay with pulsing GAME OVER."""
        overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        pulse = 0.6 + 0.4 * math.sin(self._frame_count * 0.025)
        alpha = int(180 + 75 * pulse)
        pulsed = pygame.Color(*COLORS["TEXT_GAME_OVER"][:3], alpha)

        cx = self.cfg.WINDOW_WIDTH // 2
        cy = self.cfg.WINDOW_HEIGHT // 2

        box_w, box_h = 350, 200
        box_r = pygame.Rect(cx - box_w // 2, cy - box_h // 2, box_w, box_h)

        pygame.draw.rect(self.screen, (10, 5, 8), box_r)
        pygame.draw.rect(self.screen, COLORS["TEXT_GAME_OVER"], box_r, width=2)

        # Inner highlight
        inner_box = box_r.inflate(-4, -4)
        pygame.draw.rect(self.screen, (40, 10, 20), inner_box, width=1)

        self._draw_text_centered("GAME OVER", cx, cy - 55, pulsed, 26)
        self._draw_text_centered(f"Score: {score}", cx, cy - 14,
                                 COLORS["PANEL_ACCENT"], 14)
        self._draw_text_centered("Press R to restart or ESC to quit", cx, cy + 45,
                                 COLORS["TEXT_PRIMARY"], 9)

    # ── Text helpers ──────────────────────────────────────────────────────

    def _draw_text(self, text: str, x: int, y: int, color, size: int) -> None:
        font = _get_font("press_start", size)
        surface = font.render(text, True, color)
        self.screen.blit(surface, (x, y))

    def _draw_text_centered(self, text: str, cx: int, cy: int, color, size: int) -> None:
        font = _get_font("press_start", size)
        surface = font.render(text, True, color)
        rect = surface.get_rect(center=(cx, cy))
        self.screen.blit(surface, rect)
