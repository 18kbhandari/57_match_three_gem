from __future__ import annotations

import time
import pygame

from .board import Board, GRID_SIZE

BOARD_X = 40
BOARD_Y = 80
CELL = 60

GEM_COLORS = [
    (235, 87, 87),
    (87, 166, 255),
    (97, 194, 103),
    (245, 193, 79),
    (170, 105, 220),
    (57, 201, 190),
]


class GameEngine:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.reset()

    def reset(self):
        self.board = Board()
        self.score = 0
        self.moves_remaining = 20
        self.selected = None
        self.idle_start = time.time()
        self.hint_pair = None
        self.combo = 1
        self.message = ""

    def handle_click(self, pos):
        col = (pos[0] - BOARD_X) // CELL
        row = (pos[1] - BOARD_Y) // CELL

        if not (0 <= row < GRID_SIZE and 0 <= col < GRID_SIZE):
            return

        self.idle_start = time.time()
        self.hint_pair = None

        if self.selected is None:
            self.selected = (row, col)
            return

        if not self._adjacent(self.selected, (row, col)):
            self.selected = (row, col)
            return

        first = self.selected
        second = (row, col)
        self.selected = None
        self.attempt_swap(first, second)

    def _adjacent(self, a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1]) == 1

    def attempt_swap(self, pos1, pos2):
        self.board.swap(pos1, pos2)
        matches = self.board.find_matches()

        if not matches:
            self.board.swap(pos1, pos2)
            return False

        self.moves_remaining -= 1
        self.combo = 1
        self.resolve_turn(matches)
        return True

    def resolve_turn(self, initial_matches):
        matches = initial_matches
        cascade = 0

        while matches:
            cascade += 1

            specials_created = self.board.make_specials_from_matches(matches)

            expanded = self.board.activate_specials(matches)
            cleared = len(expanded)

            if cascade == 1:
                multiplier = 1
            else:
                multiplier = cascade

            self.score += cleared * 10 * multiplier

            preserved = set(specials_created)
            self.board.clear_matches(expanded - preserved)
            self.board.drop_and_refill()

            matches = self.board.find_matches()

        self.combo = cascade

    def find_hint(self):
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                if c + 1 < GRID_SIZE:
                    self.board.swap((r, c), (r, c + 1))
                    ok = bool(self.board.find_matches())
                    self.board.swap((r, c), (r, c + 1))
                    if ok:
                        return ((r, c), (r, c + 1))
                if r + 1 < GRID_SIZE:
                    self.board.swap((r, c), (r + 1, c))
                    ok = bool(self.board.find_matches())
                    self.board.swap((r, c), (r + 1, c))
                    if ok:
                        return ((r, c), (r + 1, c))
        return None

    def update(self):
        if time.time() - self.idle_start > 5 and self.hint_pair is None:
            self.hint_pair = self.find_hint()

    def render(self, screen):
        screen.fill((24, 28, 36))

        title = pygame.font.SysFont(None, 34)
        text = title.render(
            f"SCORE: {self.score}    MOVES LEFT: {self.moves_remaining}",
            True,
            (235, 235, 235),
        )
        screen.blit(text, (40, 25))

        pulse = (time.time() * 4) % 2
        pulse_alpha = int(80 + 90 * abs(1 - pulse))

        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                gem = self.board.grid[r][c]
                if gem < 0:
                    continue

                rect = pygame.Rect(BOARD_X + c * CELL, BOARD_Y + r * CELL, CELL - 4, CELL - 4)
                color = GEM_COLORS[gem]
                pygame.draw.rect(screen, color, rect, border_radius=10)

                if self.board.specials[r][c]:
                    pygame.draw.rect(screen, (255, 255, 255), rect.inflate(-8, -8), width=4, border_radius=8)

        if self.selected:
            r, c = self.selected
            rect = pygame.Rect(BOARD_X + c * CELL, BOARD_Y + r * CELL, CELL - 4, CELL - 4)
            pygame.draw.rect(screen, (255, 255, 255), rect.inflate(6, 6), width=3)

        if self.hint_pair:
            for r, c in self.hint_pair:
                rect = pygame.Rect(BOARD_X + c * CELL, BOARD_Y + r * CELL, CELL - 4, CELL - 4)
                pygame.draw.rect(screen, (255, 255, 255), rect.inflate(8, 8), width=3)
            if int(time.time() * 4) % 2 == 0:
                for r, c in self.hint_pair:
                    rect = pygame.Rect(BOARD_X + c * CELL, BOARD_Y + r * CELL, CELL - 4, CELL - 4)
                    pygame.draw.rect(screen, (255, 255, 255), rect, width=2)

        if self.score >= 500:
            banner = title.render("STAGE CLEARED!", True, (255, 220, 100))
            screen.blit(banner, (190, 560))
        elif self.moves_remaining <= 0:
            banner = title.render("OUT OF MOVES!", True, (255, 120, 120))
            screen.blit(banner, (190, 560))
