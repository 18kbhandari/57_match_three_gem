from __future__ import annotations

import random
from typing import List, Tuple

GRID_SIZE = 8

Gem = int
Position = Tuple[int, int]


class Board:
    def __init__(self):
        self.grid: List[List[Gem]] = [
            [random.randint(0, 5) for _ in range(GRID_SIZE)]
            for _ in range(GRID_SIZE)
        ]
        self.specials = [[False for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self._remove_initial_matches()

    def _remove_initial_matches(self):
        while self.find_matches():
            for r, c in self.find_matches():
                self.grid[r][c] = random.randint(0, 5)

    def swap(self, p1: Position, p2: Position):
        (r1, c1), (r2, c2) = p1, p2
        self.grid[r1][c1], self.grid[r2][c2] = self.grid[r2][c2], self.grid[r1][c1]
        self.specials[r1][c1], self.specials[r2][c2] = self.specials[r2][c2], self.specials[r1][c1]

    def find_matches(self):
        matches = set()

        for r in range(GRID_SIZE):
            c = 0
            while c < GRID_SIZE:
                start = c
                while c + 1 < GRID_SIZE and self.grid[r][c] == self.grid[r][c + 1]:
                    c += 1
                if self.grid[r][start] >= 0 and c - start + 1 >= 3:
                    for cc in range(start, c + 1):
                        matches.add((r, cc))
                c += 1

        for c in range(GRID_SIZE):
            r = 0
            while r < GRID_SIZE:
                start = r
                while r + 1 < GRID_SIZE and self.grid[r][c] == self.grid[r + 1][c]:
                    r += 1
                if self.grid[start][c] >= 0 and r - start + 1 >= 3:
                    for rr in range(start, r + 1):
                        matches.add((rr, c))
                r += 1

        return matches

    def find_matches_with_specials(self):
        return self.find_matches()

    def drop_and_refill(self):
        for c in range(GRID_SIZE):
            write = GRID_SIZE - 1
            for r in range(GRID_SIZE - 1, -1, -1):
                if self.grid[r][c] >= 0:
                    self.grid[write][c] = self.grid[r][c]
                    self.specials[write][c] = self.specials[r][c]
                    write -= 1

            while write >= 0:
                self.grid[write][c] = random.randint(0, 5)
                self.specials[write][c] = False
                write -= 1

    def clear_matches(self, matches):
        for r, c in matches:
            self.grid[r][c] = -1
            self.specials[r][c] = False

    def make_specials_from_matches(self, matches, preferred_position=None):
        specials_created = []
        for r in range(GRID_SIZE):
            cols = [c for rr, c in matches if rr == r]
            if len(cols) >= 4:
                c = preferred_position[1] if preferred_position and preferred_position[0] == r else cols[len(cols) // 2]
                if c in cols:
                    self.specials[r][c] = True
                    specials_created.append((r, c))
            rows = [rr for rr, cc in matches if cc == r]
            if len(rows) >= 4:
                rr = preferred_position[0] if preferred_position and preferred_position[1] == r else rows[len(rows) // 2]
                if rr in rows:
                    self.specials[rr][r] = True
                    specials_created.append((rr, r))
        return specials_created

    def activate_specials(self, matches):
        expanded = set(matches)
        queue = list(matches)

        while queue:
            r, c = queue.pop()
            if 0 <= r < GRID_SIZE and 0 <= c < GRID_SIZE and self.specials[r][c]:
                for cc in range(GRID_SIZE):
                    if (r, cc) not in expanded:
                        expanded.add((r, cc))
                        queue.append((r, cc))
                for rr in range(GRID_SIZE):
                    if (rr, c) not in expanded:
                        expanded.add((rr, c))
                        queue.append((rr, c))

        return expanded
