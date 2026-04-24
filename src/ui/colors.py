"""
Colour palette — **CYBER BLUE** theme.

Deep indigo / electric blue / cyan on dark navy.
Cool, clean, pulsing with blue neon.
"""

import pygame

COLORS: dict[str, pygame.Color] = {
    # Backgrounds
    "BACKGROUND": pygame.Color("#0a0a14"),
    "BOARD_BG": pygame.Color("#0d0d1a"),
    "BOARD_BG_GAME_OVER": pygame.Color("#0a0408"),
    "PANEL_BG": pygame.Color("#080812"),
    "GAME_OVER_OVERLAY": pygame.Color(0, 0, 0, 180),

    # Text
    "TEXT_PRIMARY": pygame.Color("#d0e0f0"),
    "TEXT_ACCENT": pygame.Color("#00d4ff"),   # bright cyan
    "TEXT_DIM": pygame.Color("#334466"),
    "TEXT_GAME_OVER": pygame.Color("#ff3355"), # red-pink for contrast

    # UI elements
    "BORDER": pygame.Color("#1a2a4a"),
    "GRID_LINE": pygame.Color("#151828"),
    "GHOST": pygame.Color(0, 150, 255, 50),
    "BUTTON_DANGER": pygame.Color("#881122"),

    # Panel accents
    "PANEL_ACCENT": pygame.Color("#4488ff"),   # electric blue
    "BOARD_GLOW": pygame.Color("#0066ff"),     # deep blue for board border glow

    # Scanline overlay
    "SCANLINE": pygame.Color(0, 0, 0, 22),
}
