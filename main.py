"""
Tetris Clone — A classic Tetris game built with PyGame.

Entry point for the application. Initialises the game and starts the main loop.
"""

import sys
import pygame

from src.utils.config import Config
from src.game.game_loop import GameLoop


def main() -> None:
    """Initialise and run the Tetris game."""
    config = Config()

    pygame.init()
    pygame.display.set_caption(config.WINDOW_TITLE)

    screen = pygame.display.set_mode(
        (config.WINDOW_WIDTH, config.WINDOW_HEIGHT),
    )
    clock = pygame.time.Clock()

    game = GameLoop(screen, clock, config)
    game.run()

    pygame.quit()
    sys.exit(0)


if __name__ == "__main__":
    main()
