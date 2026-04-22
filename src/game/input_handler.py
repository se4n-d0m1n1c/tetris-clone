"""
Input handler — maps keyboard events to game actions.

Decoupled from the game loop so key bindings can be remapped independently.
"""

from __future__ import annotations

import pygame


class InputAction:
    """Enum-like namespace for actions triggered by input."""

    MOVE_LEFT = "move_left"
    MOVE_RIGHT = "move_right"
    SOFT_DROP = "soft_drop"
    HARD_DROP = "hard_drop"
    ROTATE_CW = "rotate_cw"
    ROTATE_CCW = "rotate_ccw"
    PAUSE = "pause"
    RESTART = "restart"
    QUIT = "quit"
    HOLD = "hold"


class InputHandler:
    """Reads pygame events and returns a list of actions for this frame."""

    # Default key bindings
    KEY_MAP: dict[int, str] = {
        pygame.K_LEFT: InputAction.MOVE_LEFT,
        pygame.K_RIGHT: InputAction.MOVE_RIGHT,
        pygame.K_DOWN: InputAction.SOFT_DROP,
        pygame.K_SPACE: InputAction.HARD_DROP,
        pygame.K_UP: InputAction.ROTATE_CW,
        pygame.K_x: InputAction.ROTATE_CCW,
        pygame.K_z: InputAction.ROTATE_CCW,
        pygame.K_p: InputAction.PAUSE,
        pygame.K_ESCAPE: InputAction.PAUSE,
        pygame.K_r: InputAction.RESTART,
        pygame.K_c: InputAction.HOLD,
        pygame.K_LSHIFT: InputAction.HOLD,
    }

    def __init__(self) -> None:
        # DAS (Delayed Auto-Shift) state
        self._das_delay: int = 170   # ms before auto-repeat kicks in
        self._das_rate: int = 50     # ms between auto-repeat moves
        self._das_timer: float = 0.0
        self._das_active: bool = False
        self._das_key: str | None = None

    def get_actions(self, events: list[pygame.event.Event], dt: float) -> list[str]:
        """Process a frame's worth of events and return triggered actions.

        Handles both discrete key-down events and DAS for held keys.
        """
        actions: list[str] = []
        pressed = pygame.key.get_pressed()

        # ── Discrete events (single-fire per press) ─────────────────────
        for event in events:
            if event.type == pygame.KEYDOWN:
                action = self.KEY_MAP.get(event.key)
                if action == InputAction.HARD_DROP:
                    actions.append(action)
                    self._reset_das()
                elif action == InputAction.ROTATE_CW:
                    actions.append(action)
                elif action == InputAction.ROTATE_CCW:
                    actions.append(action)
                elif action == InputAction.PAUSE:
                    actions.append(action)
                elif action == InputAction.RESTART:
                    actions.append(action)
                elif action == InputAction.HOLD:
                    actions.append(action)
                elif action == InputAction.QUIT:
                    actions.append(action)
                elif action in (InputAction.MOVE_LEFT, InputAction.MOVE_RIGHT):
                    actions.append(action)
                    self._reset_das()
                    self._das_key = action
                    self._das_active = True

            elif event.type == pygame.KEYUP:
                key_action = self.KEY_MAP.get(event.key)
                if key_action in (InputAction.MOVE_LEFT, InputAction.MOVE_RIGHT):
                    if self._das_key == key_action:
                        self._reset_das()

            elif event.type == pygame.QUIT:
                actions.append(InputAction.QUIT)

        # ── DAS auto-repeat ─────────────────────────────────────────────
        if self._das_active and self._das_key:
            if pressed[pygame.K_LEFT] or pressed[pygame.K_RIGHT]:
                self._das_timer += dt * 1000  # convert to ms
                if self._das_timer >= self._das_delay:
                    interval = self._das_rate
                    elapsed = self._das_timer - self._das_delay
                    repeats = int(elapsed / interval) + 1
                    prev = int((elapsed - interval) / interval) + 1 if elapsed >= interval else 0
                    for _ in range(repeats - prev):
                        actions.append(self._das_key)
            else:
                self._reset_das()

        # ── Soft drop (continuous) ──────────────────────────────────────
        if pressed[pygame.K_DOWN]:
            actions.append(InputAction.SOFT_DROP)

        return actions

    def _reset_das(self) -> None:
        self._das_timer = 0.0
        self._das_active = False
        self._das_key = None
