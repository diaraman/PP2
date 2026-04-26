from __future__ import annotations

import argparse
import random
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import pygame


# Screen and gameplay constants are kept in one place so the board is easy to tweak.
CELL_SIZE = 28
GRID_SIZE = 20
BOARD_SIZE = CELL_SIZE * GRID_SIZE
HUD_HEIGHT = 90
SCREEN_WIDTH = BOARD_SIZE
SCREEN_HEIGHT = BOARD_SIZE + HUD_HEIGHT
FPS = 60

ROOT = Path(__file__).resolve().parent

BG_COLOR = (18, 24, 18)
BOARD_COLOR = (34, 52, 34)
GRID_COLOR = (46, 68, 46)
TEXT_COLOR = (240, 245, 240)
SUBTEXT_COLOR = (190, 205, 190)
SNAKE_COLOR = (92, 220, 160)
SNAKE_HEAD_COLOR = (128, 245, 190)
FOOD_TYPES = (
    {"points": 1, "weight": 58, "color": (235, 84, 108), "lifetime_ms": 7000},
    {"points": 2, "weight": 26, "color": (255, 155, 173), "lifetime_ms": 6000},
    {"points": 3, "weight": 10, "color": (246, 208, 96), "lifetime_ms": 5000},
)

TARGET_FOOD_COUNT = 3
LEVEL_STEP = 3
BASE_MOVE_DELAY_MS = 180
MIN_MOVE_DELAY_MS = 80

Point = tuple[int, int]


@dataclass(slots=True)
class Food:
    # Each food item knows where it is, how many points it gives, and when it expires.
    cell: Point
    points: int
    color: tuple[int, int, int]
    expires_at: int


def load_font(size: int, bold: bool = False) -> pygame.font.Font:
    for name in ("Avenir Next", "Arial", "DejaVu Sans", None):
        try:
            return pygame.font.SysFont(name, size, bold=bold)
        except Exception:
            continue
    return pygame.font.Font(None, size)


def parse_args(argv: Iterable[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Practice 11 Snake")
    parser.add_argument("--headless", action="store_true", help="Run without opening a real window")
    parser.add_argument("--max-frames", type=int, default=0, help="Stop after N frames")
    return parser.parse_args(list(argv))


class SnakeGame:
    def __init__(self, headless: bool = False) -> None:
        if headless:
            import os

            os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
            os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

        # Pygame must be initialized before creating the window or fonts.
        pygame.init()
        pygame.display.set_caption("Practice 11 - Snake")
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.title_font = load_font(36, bold=True)
        self.font = load_font(24, bold=True)
        self.small_font = load_font(18)

        self.running = True
        self.frames = 0
        self.max_frames = 0

        self.reset_run()

    def reset_run(self) -> None:
        # Start the snake in the middle so there is room to move in every direction.
        mid = GRID_SIZE // 2
        now = pygame.time.get_ticks()
        self.snake: list[Point] = [(mid, mid), (mid - 1, mid), (mid - 2, mid)]
        self.direction: Point = (1, 0)
        self.next_direction: Point = (1, 0)
        self.foods: list[Food] = []
        self.score = 0
        self.level = 1
        self.game_over = False
        self.last_move_at = now
        self.message = "Catch the food."
        self.spawn_initial_foods()

    def grid_cells(self) -> Iterable[Point]:
        for x in range(GRID_SIZE):
            for y in range(GRID_SIZE):
                yield (x, y)

    def in_bounds(self, cell: Point) -> bool:
        return 0 <= cell[0] < GRID_SIZE and 0 <= cell[1] < GRID_SIZE

    def occupied_cells(self) -> set[Point]:
        # Food must never spawn on top of the snake or another food item.
        blocked = set(self.snake)
        blocked.update(food.cell for food in self.foods)
        return blocked

    def random_empty_cell(self) -> Point:
        blocked = self.occupied_cells()
        candidates = [cell for cell in self.grid_cells() if cell not in blocked]
        return random.choice(candidates) if candidates else (0, 0)

    def choose_food_type(self) -> dict[str, object]:
        weights = [item["weight"] for item in FOOD_TYPES]
        return random.choices(list(FOOD_TYPES), weights=weights, k=1)[0]

    def spawn_food(self) -> None:
        # Pick one of the weighted food types and place it on a free cell.
        kind = self.choose_food_type()
        now = pygame.time.get_ticks()
        self.foods.append(
            Food(
                cell=self.random_empty_cell(),
                points=int(kind["points"]),
                color=kind["color"],
                expires_at=now + int(kind["lifetime_ms"]),
            )
        )

    def spawn_initial_foods(self) -> None:
        while len(self.foods) < TARGET_FOOD_COUNT:
            self.spawn_food()

    def remove_expired_foods(self, now: int) -> None:
        self.foods = [food for food in self.foods if food.expires_at > now]

    def food_at(self, cell: Point) -> Food | None:
        for food in self.foods:
            if food.cell == cell:
                return food
        return None

    def base_move_delay_ms(self) -> int:
        return max(MIN_MOVE_DELAY_MS, BASE_MOVE_DELAY_MS - (self.level - 1) * 12)

    def update_level(self) -> None:
        self.level = max(1, self.score // LEVEL_STEP + 1)

    def set_next_direction(self, candidate: Point) -> None:
        if candidate[0] == -self.direction[0] and candidate[1] == -self.direction[1]:
            return
        self.next_direction = candidate

    def handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_q, pygame.K_ESCAPE):
                    self.running = False
                elif event.key == pygame.K_r and self.game_over:
                    self.reset_run()
                elif event.key in (pygame.K_LEFT, pygame.K_a):
                    self.set_next_direction((-1, 0))
                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    self.set_next_direction((1, 0))
                elif event.key in (pygame.K_UP, pygame.K_w):
                    self.set_next_direction((0, -1))
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    self.set_next_direction((0, 1))

    def finish_game(self) -> None:
        self.game_over = True
        self.message = "Game over. Press R to restart."

    def update(self) -> None:
        if self.game_over:
            return

        now = pygame.time.get_ticks()
        # Remove expired food, then refill the board back to the target count.
        self.remove_expired_foods(now)
        while len(self.foods) < TARGET_FOOD_COUNT:
            self.spawn_food()

        self.update_level()
        if now - self.last_move_at < self.base_move_delay_ms():
            return

        self.last_move_at = now
        self.direction = self.next_direction

        head_x, head_y = self.snake[0]
        next_head = (head_x + self.direction[0], head_y + self.direction[1])
        will_eat = self.food_at(next_head) is not None
        # When the snake is eating, the tail will not move, so the full body can block the head.
        body_to_check = self.snake if will_eat else self.snake[:-1]

        if not self.in_bounds(next_head) or next_head in body_to_check:
            self.finish_game()
            return

        self.snake.insert(0, next_head)

        food = self.food_at(next_head)
        if food is not None:
            self.foods = [item for item in self.foods if item.cell != next_head]
            self.score += food.points
            self.update_level()
            self.message = f"+{food.points} points"
            while len(self.foods) < TARGET_FOOD_COUNT:
                self.spawn_food()

        if not will_eat:
            self.snake.pop()

    def draw_background(self) -> None:
        self.screen.fill(BG_COLOR)
        pygame.draw.rect(self.screen, BOARD_COLOR, (0, HUD_HEIGHT, SCREEN_WIDTH, BOARD_SIZE))

    def draw_grid(self) -> None:
        for x in range(GRID_SIZE + 1):
            px = x * CELL_SIZE
            pygame.draw.line(self.screen, GRID_COLOR, (px, HUD_HEIGHT), (px, HUD_HEIGHT + BOARD_SIZE))
        for y in range(GRID_SIZE + 1):
            py = HUD_HEIGHT + y * CELL_SIZE
            pygame.draw.line(self.screen, GRID_COLOR, (0, py), (BOARD_SIZE, py))

    def cell_to_screen(self, cell: Point) -> tuple[int, int]:
        return cell[0] * CELL_SIZE, HUD_HEIGHT + cell[1] * CELL_SIZE

    def draw_foods(self) -> None:
        now = pygame.time.get_ticks()
        for food in self.foods:
            x, y = self.cell_to_screen(food.cell)
            rect = pygame.Rect(x + 4, y + 4, CELL_SIZE - 8, CELL_SIZE - 8)
            pygame.draw.rect(self.screen, food.color, rect, border_radius=8)
            remaining = max(0, food.expires_at - now)
            if remaining <= 2000:
                label = self.small_font.render(str(max(1, (remaining + 999) // 1000)), True, (20, 20, 20))
                self.screen.blit(label, label.get_rect(center=rect.center))

    def draw_snake(self) -> None:
        for index, cell in enumerate(reversed(self.snake)):
            actual_index = len(self.snake) - 1 - index
            x, y = self.cell_to_screen(cell)
            rect = pygame.Rect(x + 3, y + 3, CELL_SIZE - 6, CELL_SIZE - 6)
            color = SNAKE_HEAD_COLOR if actual_index == 0 else SNAKE_COLOR
            if actual_index > 0:
                fade = min(40, actual_index * 3)
                color = (
                    max(40, color[0] - fade),
                    max(80, color[1] - fade),
                    max(70, color[2] - fade),
                )
            pygame.draw.rect(self.screen, color, rect, border_radius=8)

    def draw_hud(self) -> None:
        pygame.draw.rect(self.screen, (14, 18, 14), (0, 0, SCREEN_WIDTH, HUD_HEIGHT))
        title = self.title_font.render("Snake", True, TEXT_COLOR)
        stats = self.small_font.render(
            f"Score: {self.score}   Level: {self.level}   Length: {len(self.snake)}",
            True,
            SUBTEXT_COLOR,
        )
        help_text = self.small_font.render("Arrows/WASD move   R restart   Q/Esc quit", True, SUBTEXT_COLOR)
        self.screen.blit(title, (16, 10))
        self.screen.blit(stats, (16, 42))
        self.screen.blit(help_text, (16, 62))
        if self.message:
            message = self.small_font.render(self.message, True, (180, 205, 255))
            self.screen.blit(message, (SCREEN_WIDTH - message.get_width() - 16, 18))

    def draw_game_over(self) -> None:
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 120))
        self.screen.blit(overlay, (0, 0))
        panel = pygame.Rect(0, 0, 340, 170)
        panel.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        pygame.draw.rect(self.screen, (22, 28, 22), panel, border_radius=16)
        pygame.draw.rect(self.screen, (120, 160, 120), panel, width=2, border_radius=16)
        title = self.title_font.render("Game Over", True, TEXT_COLOR)
        score = self.font.render(f"Score: {self.score}", True, TEXT_COLOR)
        level = self.font.render(f"Level reached: {self.level}", True, TEXT_COLOR)
        retry = self.small_font.render("Press R to restart", True, SUBTEXT_COLOR)
        self.screen.blit(title, title.get_rect(center=(panel.centerx, panel.y + 34)))
        self.screen.blit(score, (panel.x + 24, panel.y + 72))
        self.screen.blit(level, (panel.x + 24, panel.y + 104))
        self.screen.blit(retry, retry.get_rect(center=(panel.centerx, panel.y + 138)))

    def draw(self) -> None:
        self.draw_background()
        self.draw_hud()
        self.draw_grid()
        self.draw_foods()
        self.draw_snake()
        if self.game_over:
            self.draw_game_over()
        pygame.display.flip()

    def run(self, max_frames: int = 0) -> None:
        self.max_frames = max_frames
        while self.running:
            self.clock.tick(FPS)
            self.handle_events()
            self.update()
            self.draw()
            self.frames += 1
            if self.max_frames and self.frames >= self.max_frames:
                self.running = False
        pygame.quit()


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    game = SnakeGame(headless=args.headless)
    game.run(max_frames=args.max_frames)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
