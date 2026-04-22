"""
Colour palette for the entire application.

Centralised so theme changes are a single-file edit.
"""

import pygame

COLORS: dict[str, pygame.Color] = {
    # Backgrounds
    "BACKGROUND": pygame.Color("#1a1a2e"),
    "BOARD_BG": pygame.Color("#16213e"),
    "PANEL_BG": pygame.Color("#0f3460"),
    "GAME_OVER_OVERLAY": pygame.Color(0, 0, 0, 180),

    # Text
    "TEXT_PRIMARY": pygame.Color("#e0e0e0"),
    "TEXT_ACCENT": pygame.Color("#00d4ff"),
    "TEXT_DIM": pygame.Color("#555555"),
    "TEXT_GAME_OVER": pygame.Color("#ff4757"),

    # UI elements
    "BORDER": pygame.Color("#3a3a5c"),
    "GRID_LINE": pygame.Color("#2a2a4a"),
    "GHOST": pygame.Color(255, 255, 255, 80),
    "BUTTON_DANGER": pygame.Color("#c0392b"),
}
