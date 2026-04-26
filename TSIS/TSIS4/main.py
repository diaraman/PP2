from __future__ import annotations

import argparse
import json
import os
import random
import string
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

HEADLESS_MODE = "--headless" in sys.argv
if HEADLESS_MODE:
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

try:
    import psycopg2  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    psycopg2 = None

import pygame


# Core board constants for the Snake grid and HUD layout.
FPS = 60
CELL_SIZE = 28
GRID_SIZE = 20
BOARD_SIZE = GRID_SIZE * CELL_SIZE
SCREEN_WIDTH = 760
SCREEN_HEIGHT = 820
HUD_HEIGHT = 112
BOARD_LEFT = (SCREEN_WIDTH - BOARD_SIZE) // 2
BOARD_TOP = 132
BOARD_RECT = pygame.Rect(BOARD_LEFT, BOARD_TOP, BOARD_SIZE, BOARD_SIZE)

ROOT = Path(__file__).resolve().parent
SETTINGS_FILE = ROOT / "settings.json"
LEADERBOARD_FILE = ROOT / "leaderboard.json"
MUSIC_FILE = ROOT / "assets" / "music.mp3"

BG_TOP = (28, 82, 48)
BG_BOTTOM = (18, 60, 35)
BOARD_FILL = (24, 92, 52)
BOARD_EDGE = (150, 210, 136)
GRID_LINE = (49, 126, 74)
TEXT_MAIN = (242, 248, 242)
TEXT_SUB = (205, 227, 208)
PANEL_BG = (20, 38, 26, 225)
PANEL_EDGE = (168, 222, 156)

SNAKE_COLOR_OPTIONS = [
    (70, 145, 255),
    (88, 214, 170),
    (120, 220, 255),
    (255, 170, 90),
    (255, 140, 160),
]
SNAKE_COLOR_NAMES = {
    (70, 145, 255): "Blue",
    (88, 214, 170): "Mint",
    (120, 220, 255): "Cyan",
    (255, 170, 90): "Orange",
    (255, 140, 160): "Pink",
}

BLUE_DARK = (26, 68, 156)
FOOD_RED = (232, 78, 104)
FOOD_PINK = (255, 146, 170)
FOOD_GOLD = (244, 205, 84)
FOOD_POISON = (110, 20, 30)

FOOD_TYPES = (
    {"kind": "apple", "points": 1, "weight": 58, "color": FOOD_RED, "lifetime_ms": 7000},
    {"kind": "berry", "points": 2, "weight": 26, "color": FOOD_PINK, "lifetime_ms": 6000},
    {"kind": "gold", "points": 3, "weight": 10, "color": FOOD_GOLD, "lifetime_ms": 5000},
    {"kind": "poison", "points": 0, "weight": 6, "color": FOOD_POISON, "lifetime_ms": 6500},
)

POWERUP_TYPES = (
    {"kind": "speed_boost", "label": "S", "color": (120, 225, 255), "duration_ms": 5000},
    {"kind": "slow_motion", "label": "M", "color": (190, 140, 255), "duration_ms": 5000},
    {"kind": "shield", "label": "H", "color": (100, 220, 150), "duration_ms": 0},
)

TARGET_FOOD_COUNT = 3
LEVEL_SCORE_STEP = 3
BASE_MOVE_DELAY_MS = 170
MIN_MOVE_DELAY_MS = 80
POWERUP_FIELD_LIFETIME_MS = 8000

Point = tuple[int, int]
Button = tuple[pygame.Rect, str, str]


def load_json(path: Path, default: object) -> object:
    if not path.exists():
        return default
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def save_json(path: Path, data: object) -> None:
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def load_font(size: int, bold: bool = False) -> pygame.font.Font:
    for name in ("Avenir Next", "Arial", "DejaVu Sans", None):
        try:
            return pygame.font.SysFont(name, size, bold=bold)
        except Exception:
            continue
    return pygame.font.Font(None, size)


def sanitize_username(text: str) -> str:
    cleaned = "".join(ch for ch in text if ch.isalnum() or ch in "_- ").strip()
    return cleaned[:20] or "Player"


@dataclass(slots=True)
class Settings:
    snake_color: tuple[int, int, int] = (70, 145, 255)
    grid_overlay: bool = True
    sound_enabled: bool = True

    @classmethod
    def from_mapping(cls, data: object) -> "Settings":
        # Convert raw JSON data into a typed Settings object.
        mapping = data if isinstance(data, dict) else {}
        raw_color = mapping.get("snake_color", (70, 145, 255))
        snake_color = cls._parse_color(raw_color)
        return cls(
            snake_color=snake_color,
            grid_overlay=bool(mapping.get("grid_overlay", True)),
            sound_enabled=bool(mapping.get("sound_enabled", True)),
        )

    @staticmethod
    def _parse_color(value: object) -> tuple[int, int, int]:
        if isinstance(value, str):
            named = {
                "blue": (70, 145, 255),
                "green": (88, 214, 170),
                "cyan": (120, 220, 255),
                "orange": (255, 170, 90),
                "pink": (255, 140, 160),
            }
            return named.get(value.lower(), (70, 145, 255))
        if isinstance(value, (list, tuple)) and len(value) == 3:
            try:
                return tuple(max(0, min(255, int(v))) for v in value)  # type: ignore[return-value]
            except Exception:
                return (70, 145, 255)
        return (70, 145, 255)

    def to_mapping(self) -> dict[str, object]:
        return {
            "snake_color": list(self.snake_color),
            "grid_overlay": self.grid_overlay,
            "sound_enabled": self.sound_enabled,
        }


@dataclass(slots=True)
class Food:
    cell: Point
    kind: str
    points: int
    color: tuple[int, int, int]
    expires_at: int


@dataclass(slots=True)
class PowerUp:
    cell: Point
    kind: str
    label: str
    color: tuple[int, int, int]
    expires_at: int
    duration_ms: int


@dataclass(slots=True)
class Obstacle:
    cell: Point


@dataclass(slots=True)
class LeaderboardEntry:
    username: str
    score: int
    level_reached: int
    played_at: str

    @classmethod
    def from_mapping(cls, data: object) -> "LeaderboardEntry | None":
        if not isinstance(data, dict):
            return None
        try:
            username = str(data.get("username", data.get("name", "Player")))[:20]
            score = int(data.get("score", 0))
            level_reached = int(data.get("level_reached", data.get("level", 1)))
            played_at = str(data.get("played_at", ""))
            return cls(username=username, score=score, level_reached=level_reached, played_at=played_at)
        except Exception:
            return None

    def to_mapping(self) -> dict[str, object]:
        return {
            "username": self.username,
            "score": self.score,
            "level_reached": self.level_reached,
            "played_at": self.played_at,
        }


class LeaderboardStore:
    def __init__(self) -> None:
        # Try PostgreSQL first, but keep a JSON fallback so the game still works locally.
        self.mode = "file"
        self.entries = self.load_file_entries()
        self.conn = None
        self._init_postgres()

    def _dsn_from_env(self) -> str:
        host = os.environ.get("PGHOST")
        user = os.environ.get("PGUSER")
        password = os.environ.get("PGPASSWORD")
        dbname = os.environ.get("PGDATABASE")
        port = os.environ.get("PGPORT", "5432")
        if not all((host, user, password, dbname)):
            return ""
        return f"host={host} port={port} dbname={dbname} user={user} password={password}"

    def _init_postgres(self) -> None:
        if psycopg2 is None:
            return
        dsn = os.environ.get("DATABASE_URL") or self._dsn_from_env()
        if not dsn:
            return
        try:
            self.conn = psycopg2.connect(dsn)
            self.conn.autocommit = True
            self.ensure_schema()
            self.mode = "postgres"
        except Exception:
            self.conn = None
            self.mode = "file"

    def ensure_schema(self) -> None:
        if self.conn is None:
            return
        with self.conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS players (
                    id SERIAL PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL
                );
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS game_sessions (
                    id SERIAL PRIMARY KEY,
                    player_id INTEGER REFERENCES players(id),
                    score INTEGER NOT NULL,
                    level_reached INTEGER NOT NULL,
                    played_at TIMESTAMP DEFAULT NOW()
                );
                """
            )

    def load_file_entries(self) -> list[LeaderboardEntry]:
        raw = load_json(LEADERBOARD_FILE, [])
        entries: list[LeaderboardEntry] = []
        if isinstance(raw, list):
            for item in raw:
                entry = LeaderboardEntry.from_mapping(item)
                if entry is not None:
                    entries.append(entry)
        return self.sorted_entries(entries)

    def sorted_entries(self, entries: list[LeaderboardEntry]) -> list[LeaderboardEntry]:
        return sorted(entries, key=lambda e: (e.score, e.level_reached), reverse=True)

    def persist_file_entries(self) -> None:
        save_json(LEADERBOARD_FILE, [entry.to_mapping() for entry in self.sorted_entries(self.entries)])

    def save_result(self, username: str, score: int, level_reached: int) -> None:
        # Store the run in both PostgreSQL and the local JSON cache when possible.
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        if self.mode == "postgres" and self.conn is not None:
            try:
                with self.conn.cursor() as cur:
                    cur.execute(
                        "INSERT INTO players (username) VALUES (%s) ON CONFLICT (username) DO NOTHING;",
                        (username,),
                    )
                    cur.execute("SELECT id FROM players WHERE username = %s;", (username,))
                    row = cur.fetchone()
                    if not row:
                        raise RuntimeError("player lookup failed")
                    player_id = row[0]
                    cur.execute(
                        """
                        INSERT INTO game_sessions (player_id, score, level_reached, played_at)
                        VALUES (%s, %s, %s, NOW());
                        """,
                        (player_id, score, level_reached),
                    )
            except Exception:
                self.mode = "file"
        entry = LeaderboardEntry(username=username, score=score, level_reached=level_reached, played_at=timestamp)
        self.entries.append(entry)
        self.entries = self.sorted_entries(self.entries)
        self.persist_file_entries()

    def get_top10(self) -> list[LeaderboardEntry]:
        if self.mode == "postgres" and self.conn is not None:
            try:
                with self.conn.cursor() as cur:
                    cur.execute(
                        """
                        SELECT p.username, gs.score, gs.level_reached, gs.played_at
                        FROM game_sessions gs
                        JOIN players p ON p.id = gs.player_id
                        ORDER BY gs.score DESC, gs.level_reached DESC, gs.played_at DESC
                        LIMIT 10;
                        """
                    )
                    rows = cur.fetchall()
                    return [
                        LeaderboardEntry(
                            username=str(row[0]),
                            score=int(row[1]),
                            level_reached=int(row[2]),
                            played_at=str(row[3]),
                        )
                        for row in rows
                    ]
            except Exception:
                self.mode = "file"
        if not self.entries:
            self.entries = self.load_file_entries()
        return self.sorted_entries(self.entries)[:10]

    def get_personal_best(self, username: str) -> int:
        username = username[:20]
        if self.mode == "postgres" and self.conn is not None:
            try:
                with self.conn.cursor() as cur:
                    cur.execute(
                        """
                        SELECT COALESCE(MAX(gs.score), 0)
                        FROM game_sessions gs
                        JOIN players p ON p.id = gs.player_id
                        WHERE p.username = %s;
                        """,
                        (username,),
                    )
                    row = cur.fetchone()
                    return int(row[0]) if row else 0
            except Exception:
                self.mode = "file"
        if not self.entries:
            self.entries = self.load_file_entries()
        best = 0
        for entry in self.entries:
            if entry.username == username:
                best = max(best, entry.score)
        return best


class SnakeGame:
    def __init__(self, headless: bool = False) -> None:
        if headless:
            os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
            os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

        # Initialize Pygame before creating the window, mixer, and fonts.
        pygame.init()
        pygame.display.set_caption("TSIS4 - Snake")
        self.init_music()

        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.title_font = load_font(42, bold=True)
        self.font = load_font(24, bold=True)
        self.small_font = load_font(18)

        self.running = True
        self.frames = 0
        self.max_frames = 0

        self.store = LeaderboardStore()
        self.settings = Settings.from_mapping(load_json(SETTINGS_FILE, Settings().to_mapping()))

        self.state = "menu"
        self.username = "Player"
        self.menu_input = "Player"
        self.personal_best = self.store.get_personal_best(self.username)
        self.menu_best = self.personal_best
        self.cursor_visible = True
        self.cursor_ticks = 0
        self.message = "Type a username and press Play."

        self.background = self.build_background()
        self.board_base = self.build_board_surface()

        self.menu_buttons = self.build_buttons(
            [("Play", "play"), ("Leaderboard", "leaderboard"), ("Settings", "settings"), ("Quit", "quit")],
            top=0,
            width=150,
        )
        self.leaderboard_buttons = self.build_buttons([("Back", "back")], top=0, width=180)
        self.settings_buttons = self.build_buttons(
            [("Grid", "grid"), ("Sound", "sound"), ("Color", "color"), ("Save & Back", "save_back")],
            top=0,
            width=150,
        )
        self.game_over_buttons = self.build_buttons([("Retry", "retry"), ("Quit", "quit")], top=0, width=180)

        self.reset_run()

    def init_music(self) -> None:
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            if MUSIC_FILE.exists():
                pygame.mixer.music.load(str(MUSIC_FILE))
                pygame.mixer.music.set_volume(0.35)
                pygame.mixer.music.play(-1)
        except Exception:
            pass

    def build_buttons(
        self,
        items: list[tuple[str, str]],
        top: int,
        width: int = 160,
        height: int = 46,
        gap: int = 14,
    ) -> list[Button]:
        total_width = len(items) * width + max(0, len(items) - 1) * gap
        start_x = (SCREEN_WIDTH - total_width) // 2
        buttons: list[Button] = []
        for index, (label, action) in enumerate(items):
            rect = pygame.Rect(start_x + index * (width + gap), top, width, height)
            buttons.append((rect, label, action))
        return buttons

    def build_background(self) -> pygame.Surface:
        surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        for y in range(SCREEN_HEIGHT):
            ratio = y / max(1, SCREEN_HEIGHT - 1)
            color = [
                int(BG_TOP[i] * (1 - ratio) + BG_BOTTOM[i] * ratio)
                for i in range(3)
            ]
            pygame.draw.line(surface, color, (0, y), (SCREEN_WIDTH, y))

        rng = random.Random(17)
        for _ in range(240):
            x = rng.randint(0, SCREEN_WIDTH - 1)
            y = rng.randint(0, SCREEN_HEIGHT - 1)
            radius = rng.randint(2, 7)
            tint = rng.choice([(26, 96, 54), (34, 108, 60), (20, 82, 47)])
            alpha = rng.randint(28, 58)
            dot = pygame.Surface((radius * 2 + 2, radius * 2 + 2), pygame.SRCALPHA)
            pygame.draw.circle(dot, (*tint, alpha), (radius + 1, radius + 1), radius)
            surface.blit(dot, (x - radius, y - radius))
        return surface

    def build_board_surface(self) -> pygame.Surface:
        surface = pygame.Surface((BOARD_RECT.width, BOARD_RECT.height), pygame.SRCALPHA)
        surface.fill(BOARD_FILL)
        return surface

    def reset_run(self) -> None:
        # Each run starts with a short snake in the center of the board.
        mid = GRID_SIZE // 2
        now = pygame.time.get_ticks()
        self.snake: list[Point] = [(mid, mid), (mid - 1, mid), (mid - 2, mid)]
        self.direction: Point = (1, 0)
        self.next_direction: Point = (1, 0)
        self.foods: list[Food] = []
        self.powerup: PowerUp | None = None
        self.obstacles: list[Obstacle] = []
        self.active_powerup = ""
        self.active_powerup_until = 0
        self.powerup_spawn_at = now
        self.score = 0
        self.level = 1
        self.max_level_reached = 1
        self.game_over = False
        self.last_move_at = now
        self.move_delay_ms = BASE_MOVE_DELAY_MS
        self.message = "Catch the hearts."
        self.spawn_initial_foods()

    def start_game(self) -> None:
        self.username = sanitize_username(self.menu_input)
        self.personal_best = self.store.get_personal_best(self.username)
        self.reset_run()
        self.state = "playing"
        self.message = f"Good luck, {self.username}."

    def occupied_cells(self) -> set[Point]:
        # Track every blocked tile so spawning never overlaps the snake or items.
        blocked = set(self.snake)
        blocked.update(food.cell for food in self.foods)
        blocked.update(obstacle.cell for obstacle in self.obstacles)
        if self.powerup is not None:
            blocked.add(self.powerup.cell)
        return blocked

    def random_empty_cell(self) -> Point:
        blocked = self.occupied_cells()
        for _ in range(400):
            cell = (random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1))
            if cell not in blocked:
                return cell
        return 0, 0

    def choose_food_type(self) -> dict[str, object]:
        weights = [item["weight"] for item in FOOD_TYPES]
        return random.choices(list(FOOD_TYPES), weights=weights, k=1)[0]

    def spawn_food(self) -> None:
        # Food selection is weighted, so common food appears more often than rare food.
        kind = self.choose_food_type()
        now = pygame.time.get_ticks()
        self.foods.append(
            Food(
                cell=self.random_empty_cell(),
                kind=str(kind["kind"]),
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

    def spawn_powerup(self) -> None:
        if self.powerup is not None or self.active_powerup:
            return
        now = pygame.time.get_ticks()
        kind = random.choices(list(POWERUP_TYPES), weights=[44, 34, 22], k=1)[0]
        self.powerup = PowerUp(
            cell=self.random_empty_cell(),
            kind=str(kind["kind"]),
            label=str(kind["label"]),
            color=kind["color"],
            expires_at=now + POWERUP_FIELD_LIFETIME_MS,
            duration_ms=int(kind["duration_ms"]),
        )
        self.powerup_spawn_at = now

    def update_level(self) -> None:
        new_level = max(1, self.score // LEVEL_SCORE_STEP + 1)
        if new_level > self.level:
            self.level = new_level
            self.max_level_reached = max(self.max_level_reached, self.level)
            self.obstacles = self.generate_obstacles_for_level()
            self.message = f"Level {self.level}"
        self.move_delay_ms = self.base_move_delay_ms()

    def base_move_delay_ms(self) -> int:
        return max(MIN_MOVE_DELAY_MS, BASE_MOVE_DELAY_MS - (self.level - 1) * 12)

    def effective_move_delay_ms(self, now: int) -> int:
        delay = self.base_move_delay_ms()
        if self.active_powerup == "speed_boost" and now < self.active_powerup_until:
            delay = int(delay * 0.6)
        elif self.active_powerup == "slow_motion" and now < self.active_powerup_until:
            delay = int(delay * 1.5)
        return max(MIN_MOVE_DELAY_MS, delay)

    def reachable_cells(self, blocked: set[Point]) -> set[Point]:
        start = self.snake[0]
        queue = [start]
        visited = {start}
        while queue:
            cell = queue.pop(0)
            for nx, ny in ((cell[0] + 1, cell[1]), (cell[0] - 1, cell[1]), (cell[0], cell[1] + 1), (cell[0], cell[1] - 1)):
                next_cell = (nx, ny)
                if not self.in_bounds(next_cell) or next_cell in blocked or next_cell in visited:
                    continue
                visited.add(next_cell)
                queue.append(next_cell)
        return visited

    def obstacle_layout_safe(self, obstacle_cells: list[Point]) -> bool:
        blocked = set(obstacle_cells)
        blocked.update(self.snake)
        if self.powerup is not None:
            blocked.add(self.powerup.cell)

        reachable = self.reachable_cells(blocked)
        if len(reachable) < max(12, len(self.snake) + 5):
            return False
        head_neighbors = 0
        head_x, head_y = self.snake[0]
        for nx, ny in ((head_x + 1, head_y), (head_x - 1, head_y), (head_x, head_y + 1), (head_x, head_y - 1)):
            if self.in_bounds((nx, ny)) and (nx, ny) not in blocked:
                head_neighbors += 1
        return head_neighbors >= 2

    def generate_obstacles_for_level(self) -> list[Obstacle]:
        if self.level < 3:
            return []
        count = min(3 + (self.level - 3), 9)
        blocked = self.occupied_cells()
        candidates = [cell for cell in self.grid_cells() if cell not in blocked]
        if len(candidates) <= count:
            return []
        for _ in range(180):
            picked = random.sample(candidates, count)
            if self.obstacle_layout_safe(picked):
                return [Obstacle(cell=cell) for cell in picked]
        return []

    def grid_cells(self) -> Iterable[Point]:
        for x in range(GRID_SIZE):
            for y in range(GRID_SIZE):
                yield (x, y)

    def set_next_direction(self, candidate: Point) -> None:
        if candidate == (0, 0):
            return
        if candidate[0] == -self.direction[0] and candidate[1] == -self.direction[1]:
            return
        self.next_direction = candidate

    def collect_powerup(self, powerup: PowerUp) -> None:
        # Only one active power-up can be running at a time.
        self.powerup = None
        self.powerup_spawn_at = pygame.time.get_ticks()
        if self.active_powerup:
            return
        self.active_powerup = powerup.kind
        if powerup.kind in {"speed_boost", "slow_motion"}:
            self.active_powerup_until = pygame.time.get_ticks() + powerup.duration_ms
            self.message = f"{powerup.kind.replace('_', ' ').title()} activated"
        else:
            self.active_powerup_until = 0
            self.message = "Shield armed"

    def active_powerup_text(self) -> str:
        if not self.active_powerup:
            return ""
        if self.active_powerup == "shield":
            return "Shield armed"
        remaining = max(0, self.active_powerup_until - pygame.time.get_ticks())
        return f"{self.active_powerup.replace('_', ' ').title()} {remaining / 1000:.1f}s"

    def finish_game(self) -> None:
        # Game over is handled once and then the state switches to the end screen.
        if self.game_over:
            return
        self.game_over = True
        self.state = "game_over"
        self.store.save_result(self.username, self.score, self.max_level_reached)
        self.personal_best = max(self.personal_best, self.score)
        self.message = "Game over."

    def handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                continue
            if event.type == pygame.KEYDOWN and event.key == pygame.K_q:
                self.running = False
                continue

            if self.state == "menu":
                self.handle_menu_event(event)
            elif self.state == "leaderboard":
                self.handle_leaderboard_event(event)
            elif self.state == "settings":
                self.handle_settings_event(event)
            elif self.state == "playing":
                self.handle_game_event(event)
            elif self.state == "game_over":
                self.handle_game_over_event(event)

    def handle_menu_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                self.start_game()
            elif event.key == pygame.K_ESCAPE:
                self.running = False
            elif event.key == pygame.K_BACKSPACE:
                self.menu_input = self.menu_input[:-1]
                self.menu_best = self.store.get_personal_best(sanitize_username(self.menu_input))
            else:
                ch = event.unicode
                if ch and ch in string.ascii_letters + string.digits + "_- " and len(self.menu_input) < 20:
                    self.menu_input += ch
                    self.menu_best = self.store.get_personal_best(sanitize_username(self.menu_input))
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            action = self.button_hit(self.menu_buttons, event.pos)
            if action == "play":
                self.start_game()
            elif action == "leaderboard":
                self.state = "leaderboard"
            elif action == "settings":
                self.state = "settings"
            elif action == "quit":
                self.running = False

    def handle_leaderboard_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.state = "menu"
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.button_hit(self.leaderboard_buttons, event.pos) == "back":
                self.state = "menu"

    def handle_settings_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                save_json(SETTINGS_FILE, self.settings.to_mapping())
                self.state = "menu"
            elif event.key in (pygame.K_LEFT, pygame.K_a, pygame.K_RIGHT, pygame.K_d):
                self.cycle_color()
            elif event.key in (pygame.K_UP, pygame.K_w, pygame.K_DOWN, pygame.K_s):
                self.toggle_grid()
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            action = self.button_hit(self.settings_buttons, event.pos)
            if action == "grid":
                self.toggle_grid()
            elif action == "sound":
                self.toggle_sound()
            elif action == "color":
                self.cycle_color()
            elif action == "save_back":
                save_json(SETTINGS_FILE, self.settings.to_mapping())
                self.state = "menu"

    def handle_game_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.running = False
            elif event.key == pygame.K_r:
                self.reset_run()
                self.state = "playing"
            elif event.key in (pygame.K_LEFT, pygame.K_a):
                self.set_next_direction((-1, 0))
            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                self.set_next_direction((1, 0))
            elif event.key in (pygame.K_UP, pygame.K_w):
                self.set_next_direction((0, -1))
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.set_next_direction((0, 1))

    def handle_game_over_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                self.reset_run()
                self.state = "playing"
            elif event.key == pygame.K_ESCAPE:
                self.running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            action = self.button_hit(self.game_over_buttons, event.pos)
            if action == "retry":
                self.reset_run()
                self.state = "playing"
            elif action == "quit":
                self.running = False

    def button_hit(self, buttons: list[Button], pos: tuple[int, int]) -> str:
        for rect, _, action in buttons:
            if rect.collidepoint(pos):
                return action
        return ""

    def toggle_grid(self) -> None:
        self.settings.grid_overlay = not self.settings.grid_overlay
        save_json(SETTINGS_FILE, self.settings.to_mapping())

    def toggle_sound(self) -> None:
        self.settings.sound_enabled = not self.settings.sound_enabled
        save_json(SETTINGS_FILE, self.settings.to_mapping())

    def cycle_color(self) -> None:
        current = self.settings.snake_color
        index = SNAKE_COLOR_OPTIONS.index(current) if current in SNAKE_COLOR_OPTIONS else 0
        self.settings.snake_color = SNAKE_COLOR_OPTIONS[(index + 1) % len(SNAKE_COLOR_OPTIONS)]
        save_json(SETTINGS_FILE, self.settings.to_mapping())

    def remove_expired_foods(self, now: int) -> None:
        self.foods = [food for food in self.foods if food.expires_at > now]

    def remove_expired_powerups(self, now: int) -> None:
        if self.powerup is not None and self.powerup.expires_at <= now:
            self.powerup = None
            self.powerup_spawn_at = now

        if self.active_powerup in {"speed_boost", "slow_motion"} and now >= self.active_powerup_until:
            self.active_powerup = ""
            self.active_powerup_until = 0

    def in_bounds(self, cell: Point) -> bool:
        return 0 <= cell[0] < GRID_SIZE and 0 <= cell[1] < GRID_SIZE

    def draw_background(self) -> None:
        self.screen.blit(self.background, (0, 0))

    def draw_panel(self, rect: pygame.Rect, title: str) -> None:
        panel_surface = pygame.Surface(rect.size, pygame.SRCALPHA)
        panel_surface.fill(PANEL_BG)
        self.screen.blit(panel_surface, rect.topleft)
        pygame.draw.rect(self.screen, PANEL_EDGE, rect, width=2, border_radius=18)
        head = self.title_font.render(title, True, TEXT_MAIN)
        self.screen.blit(head, (rect.x + 20, rect.y + 18))

    def draw_buttons(self, buttons: list[Button]) -> None:
        mouse = pygame.mouse.get_pos()
        for rect, label, _ in buttons:
            hovered = rect.collidepoint(mouse)
            fill = (86, 96, 122) if hovered else (52, 58, 76)
            pygame.draw.rect(self.screen, fill, rect, border_radius=12)
            pygame.draw.rect(self.screen, (115, 122, 144), rect, width=2, border_radius=12)
            text = self.small_font.render(label, True, TEXT_MAIN)
            self.screen.blit(text, text.get_rect(center=rect.center))

    def draw_grid(self) -> None:
        if not self.settings.grid_overlay:
            return
        for x in range(GRID_SIZE + 1):
            start = (BOARD_LEFT + x * CELL_SIZE, BOARD_TOP)
            end = (BOARD_LEFT + x * CELL_SIZE, BOARD_TOP + BOARD_SIZE)
            pygame.draw.line(self.screen, GRID_LINE, start, end, 1)
        for y in range(GRID_SIZE + 1):
            start = (BOARD_LEFT, BOARD_TOP + y * CELL_SIZE)
            end = (BOARD_LEFT + BOARD_SIZE, BOARD_TOP + y * CELL_SIZE)
            pygame.draw.line(self.screen, GRID_LINE, start, end, 1)

    def draw_board(self) -> None:
        self.screen.blit(self.board_base, BOARD_RECT.topleft)
        pygame.draw.rect(self.screen, BOARD_EDGE, BOARD_RECT, 3, border_radius=18)
        self.draw_grid()

    def draw_heart(self, rect: pygame.Rect, color: tuple[int, int, int]) -> None:
        heart = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        shadow = tuple(max(0, c - 36) for c in color)
        highlight = tuple(min(255, c + 35) for c in color)
        pygame.draw.circle(heart, shadow, (int(rect.width * 0.32), int(rect.height * 0.34)), int(rect.width * 0.24))
        pygame.draw.circle(heart, shadow, (int(rect.width * 0.68), int(rect.height * 0.34)), int(rect.width * 0.24))
        pygame.draw.polygon(heart, shadow, [
            (int(rect.width * 0.12), int(rect.height * 0.34)),
            (int(rect.width * 0.88), int(rect.height * 0.34)),
            (int(rect.width * 0.50), int(rect.height * 0.90)),
        ])
        pygame.draw.polygon(heart, color, [
            (int(rect.width * 0.24), int(rect.height * 0.26)),
            (int(rect.width * 0.76), int(rect.height * 0.26)),
            (int(rect.width * 0.50), int(rect.height * 0.72)),
        ])
        pygame.draw.circle(heart, highlight, (int(rect.width * 0.34), int(rect.height * 0.28)), 3)
        self.screen.blit(heart, rect.topleft)

    def draw_foods(self) -> None:
        now = pygame.time.get_ticks()
        for food in self.foods:
            x, y = self.cell_to_screen(food.cell)
            rect = pygame.Rect(x + 2, y + 2, CELL_SIZE - 4, CELL_SIZE - 4)
            self.draw_heart(rect, food.color)

            remaining = max(0, food.expires_at - now)
            if remaining <= 2000:
                label = self.small_font.render(str(max(1, (remaining + 999) // 1000)), True, (18, 20, 18))
                self.screen.blit(label, label.get_rect(center=rect.center))

            if food.kind == "poison":
                pygame.draw.circle(self.screen, (20, 20, 20), rect.center, 4)

    def draw_powerup(self) -> None:
        if self.powerup is None:
            return
        x, y = self.cell_to_screen(self.powerup.cell)
        rect = pygame.Rect(x + 2, y + 2, CELL_SIZE - 4, CELL_SIZE - 4)
        pygame.draw.rect(self.screen, self.powerup.color, rect, border_radius=8)
        pygame.draw.rect(self.screen, (255, 255, 255), rect, 2, border_radius=8)
        label = self.font.render(self.powerup.label, True, (20, 20, 20))
        self.screen.blit(label, label.get_rect(center=rect.center))
        remaining = max(0, self.powerup.expires_at - pygame.time.get_ticks())
        if remaining <= 2000:
            small = self.small_font.render(str(max(1, (remaining + 999) // 1000)), True, (20, 20, 20))
            self.screen.blit(small, small.get_rect(center=rect.center))

    def draw_obstacles(self) -> None:
        for obstacle in self.obstacles:
            x, y = self.cell_to_screen(obstacle.cell)
            rect = pygame.Rect(x + 1, y + 1, CELL_SIZE - 2, CELL_SIZE - 2)
            pygame.draw.rect(self.screen, (82, 86, 96), rect, border_radius=5)
            pygame.draw.rect(self.screen, (20, 22, 28), rect, width=2, border_radius=5)

    def draw_snake(self) -> None:
        base = self.settings.snake_color
        for index, cell in enumerate(reversed(self.snake)):
            actual_index = len(self.snake) - 1 - index
            x, y = self.cell_to_screen(cell)
            rect = pygame.Rect(x + 3, y + 3, CELL_SIZE - 6, CELL_SIZE - 6)

            if actual_index == 0:
                color = tuple(min(255, c + 35) for c in base)
            elif actual_index <= 2:
                color = base
            else:
                fade = min(30, actual_index * 2)
                color = (
                    max(40, base[0] - fade),
                    max(70, base[1] - fade),
                    max(120, base[2] - fade),
                )

            pygame.draw.rect(self.screen, color, rect, border_radius=8)
            pygame.draw.rect(self.screen, tuple(max(0, c - 18) for c in color), rect.inflate(-10, -10), border_radius=5)

        head_x, head_y = self.cell_to_screen(self.snake[0])
        head_rect = pygame.Rect(head_x + 3, head_y + 3, CELL_SIZE - 6, CELL_SIZE - 6)
        eye_y = head_rect.y + 8
        if self.direction == (1, 0):
            eyes = [(head_rect.right - 8, eye_y), (head_rect.right - 8, eye_y + 10)]
        elif self.direction == (-1, 0):
            eyes = [(head_rect.left + 8, eye_y), (head_rect.left + 8, eye_y + 10)]
        elif self.direction == (0, -1):
            eyes = [(head_rect.x + 8, head_rect.top + 6), (head_rect.right - 8, head_rect.top + 6)]
        else:
            eyes = [(head_rect.x + 8, head_rect.bottom - 8), (head_rect.right - 8, head_rect.bottom - 8)]
        for eye in eyes:
            pygame.draw.circle(self.screen, (245, 250, 248), eye, 3)
            pygame.draw.circle(self.screen, BLUE_DARK, eye, 1)

    def draw_hud(self) -> None:
        pygame.draw.rect(self.screen, (15, 17, 24), (0, 0, SCREEN_WIDTH, HUD_HEIGHT))
        pygame.draw.line(self.screen, (72, 78, 92), (0, HUD_HEIGHT - 1), (SCREEN_WIDTH, HUD_HEIGHT - 1), 2)
        title = self.title_font.render("Snake", True, TEXT_MAIN)
        stats = self.small_font.render(
            f"User: {self.username}   Score: {self.score}   Level: {self.level}   Best: {self.personal_best}",
            True,
            TEXT_SUB,
        )
        help_text = self.small_font.render("Arrows/WASD move   R restart   Esc quit", True, (150, 156, 168))
        self.screen.blit(title, (18, 10))
        self.screen.blit(stats, (18, 48))
        self.screen.blit(help_text, (18, 72))
        if self.active_powerup:
            label = self.small_font.render(f"Power-up: {self.active_powerup_text()}", True, (255, 240, 210))
            self.screen.blit(label, (300, 10))
        if self.message:
            msg = self.small_font.render(self.message, True, (180, 200, 255))
            self.screen.blit(msg, (300, 36))

    def draw_menu(self) -> None:
        self.draw_background()
        panel = pygame.Rect(0, 0, 640, 430)
        panel.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 8)

        shadow = pygame.Rect(panel.x + 6, panel.y + 8, panel.width, panel.height)
        shadow_surface = pygame.Surface(shadow.size, pygame.SRCALPHA)
        shadow_surface.fill((0, 0, 0, 60))
        self.screen.blit(shadow_surface, shadow.topleft)

        panel_surface = pygame.Surface(panel.size, pygame.SRCALPHA)
        panel_surface.fill((16, 36, 21, 230))
        self.screen.blit(panel_surface, panel.topleft)
        pygame.draw.rect(self.screen, (178, 223, 152), panel, width=2, border_radius=22)

        title = self.title_font.render("Main Menu", True, TEXT_MAIN)
        self.screen.blit(title, (panel.x + 22, panel.y + 28))

        prompt1 = self.small_font.render("Classic Snake with menu, SQL, and obstacles.", True, TEXT_SUB)
        prompt2 = self.small_font.render("Press Enter or click Play.", True, TEXT_SUB)
        self.screen.blit(prompt1, (panel.x + 22, panel.y + 94))
        self.screen.blit(prompt2, (panel.x + 22, panel.y + 128))

        label = self.small_font.render("Username", True, TEXT_SUB)
        self.screen.blit(label, (panel.x + 22, panel.y + 170))
        box = pygame.Rect(panel.x + 22, panel.y + 198, 250, 44)
        pygame.draw.rect(self.screen, (21, 48, 28), box, border_radius=10)
        pygame.draw.rect(self.screen, (120, 180, 125), box, width=2, border_radius=10)
        name_value = self.menu_input or "Player"
        if self.cursor_visible:
            name_value += "_"
        name_text = self.small_font.render(name_value[:20], True, TEXT_MAIN)
        self.screen.blit(name_text, (box.x + 14, box.y + 10))

        best_text = self.small_font.render(f"Personal best: {self.menu_best}", True, TEXT_SUB)
        self.screen.blit(best_text, (panel.x + 22, panel.y + 250))

        button_row_1 = self.build_buttons(
            [("Play", "play"), ("Leaderboard", "leaderboard")],
            top=panel.y + 300,
            width=190,
            height=44,
            gap=18,
        )
        button_row_2 = self.build_buttons(
            [("Settings", "settings"), ("Quit", "quit")],
            top=panel.y + 356,
            width=190,
            height=44,
            gap=18,
        )
        self.menu_buttons = button_row_1 + button_row_2
        self.draw_buttons(self.menu_buttons)

    def draw_leaderboard(self) -> None:
        self.draw_background()
        panel = pygame.Rect(0, 0, 620, 520)
        panel.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 16)
        self.draw_panel(panel, "Leaderboard")
        header = self.small_font.render("Rank  Username           Score   Level   Date", True, (170, 176, 190))
        self.screen.blit(header, (panel.x + 20, panel.y + 76))
        entries = self.store.get_top10()
        if not entries:
            empty = self.small_font.render("No scores yet.", True, TEXT_SUB)
            self.screen.blit(empty, (panel.x + 20, panel.y + 116))
        else:
            for idx, entry in enumerate(entries, start=1):
                row = f"{idx:<4} {entry.username:<18} {entry.score:<7} {entry.level_reached:<7} {entry.played_at}"
                text = self.small_font.render(row, True, TEXT_MAIN if idx <= 3 else (210, 214, 224))
                self.screen.blit(text, (panel.x + 20, panel.y + 112 + (idx - 1) * 34))
        self.leaderboard_buttons = self.build_buttons([("Back", "back")], top=panel.bottom - 64, width=180)
        self.draw_buttons(self.leaderboard_buttons)

    def draw_settings(self) -> None:
        self.draw_background()
        panel = pygame.Rect(0, 0, 620, 430)
        panel.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 8)
        self.draw_panel(panel, "Settings")

        lines = [
            f"Grid overlay: {'On' if self.settings.grid_overlay else 'Off'}",
            f"Sound: {'On' if self.settings.sound_enabled else 'Off'}",
            f"Snake color: {SNAKE_COLOR_NAMES.get(self.settings.snake_color, str(self.settings.snake_color))}",
            f"RGB: {self.settings.snake_color[0]}, {self.settings.snake_color[1]}, {self.settings.snake_color[2]}",
        ]
        for idx, line in enumerate(lines):
            text = self.font.render(line, True, TEXT_MAIN if idx < 2 else TEXT_SUB)
            self.screen.blit(text, (panel.x + 20, panel.y + 88 + idx * 46))

        preview = pygame.Rect(panel.right - 180, panel.y + 92, 130, 150)
        pygame.draw.rect(self.screen, (16, 18, 24), preview, border_radius=14)
        pygame.draw.rect(self.screen, (88, 98, 120), preview, width=2, border_radius=14)
        color = self.settings.snake_color
        pygame.draw.rect(self.screen, color, (preview.x + 30, preview.y + 44, 70, 36), border_radius=10)
        pygame.draw.rect(self.screen, (235, 245, 255), (preview.x + 42, preview.y + 50, 24, 12), border_radius=4)
        pygame.draw.rect(self.screen, (34, 34, 40), (preview.x + 24, preview.y + 78, 16, 12), border_radius=3)
        pygame.draw.rect(self.screen, (34, 34, 40), (preview.x + 90, preview.y + 78, 16, 12), border_radius=3)
        self.screen.blit(self.small_font.render("Click buttons or use keys.", True, TEXT_SUB), (panel.x + 20, panel.bottom - 58))

        self.settings_buttons = self.build_buttons(
            [("Grid", "grid"), ("Sound", "sound"), ("Color", "color"), ("Save & Back", "save_back")],
            top=panel.bottom - 90,
            width=150,
        )
        self.draw_buttons(self.settings_buttons)

    def draw_game_over(self) -> None:
        self.draw_gameplay()
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 155))
        self.screen.blit(overlay, (0, 0))
        panel = pygame.Rect(0, 0, 460, 250)
        panel.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.draw_panel(panel, "Game Over")
        lines = [
            f"Final score: {self.score}",
            f"Level reached: {self.max_level_reached}",
            f"Personal best: {self.personal_best}",
        ]
        for idx, line in enumerate(lines):
            text = self.font.render(line, True, TEXT_MAIN)
            self.screen.blit(text, (panel.x + 20, panel.y + 82 + idx * 34))
        self.game_over_buttons = self.build_buttons([("Retry", "retry"), ("Quit", "quit")], top=panel.bottom - 62, width=170)
        self.draw_buttons(self.game_over_buttons)

    def draw_gameplay(self) -> None:
        self.draw_background()
        self.draw_hud()
        self.draw_board()
        self.draw_obstacles()
        self.draw_foods()
        self.draw_powerup()
        self.draw_snake()

    def draw(self) -> None:
        if self.state == "menu":
            self.draw_menu()
        elif self.state == "leaderboard":
            self.draw_leaderboard()
        elif self.state == "settings":
            self.draw_settings()
        elif self.state == "playing":
            self.draw_gameplay()
        elif self.state == "game_over":
            self.draw_game_over()
        pygame.display.flip()

    def update(self, dt: float) -> None:
        # Menu and non-game states skip movement logic entirely.
        if self.state == "menu":
            self.cursor_ticks += 1
            if self.cursor_ticks >= 30:
                self.cursor_ticks = 0
                self.cursor_visible = not self.cursor_visible
            return
        if self.state != "playing":
            return

        now = pygame.time.get_ticks()
        self.remove_expired_foods(now)
        self.remove_expired_powerups(now)

        while len(self.foods) < TARGET_FOOD_COUNT:
            self.spawn_food()

        if self.powerup is None and not self.active_powerup and now - self.powerup_spawn_at >= POWERUP_FIELD_LIFETIME_MS:
            self.spawn_powerup()

        self.update_level()
        move_delay = self.effective_move_delay_ms(now)
        if now - self.last_move_at < move_delay:
            return

        self.last_move_at = now
        self.direction = self.next_direction

        # Move the head first, then decide whether the tail should shrink or stay.
        head_x, head_y = self.snake[0]
        next_head = (head_x + self.direction[0], head_y + self.direction[1])
        will_eat = self.food_at(next_head) is not None
        body_to_check = self.snake if will_eat else self.snake[:-1]
        obstacle_at_next = any(obstacle.cell == next_head for obstacle in self.obstacles)

        shield_blocked = False
        if not self.in_bounds(next_head):
            if self.active_powerup == "shield":
                next_head = (
                    min(max(next_head[0], 0), GRID_SIZE - 1),
                    min(max(next_head[1], 0), GRID_SIZE - 1),
                )
                shield_blocked = True
            else:
                self.finish_game()
                return

        if (next_head in body_to_check or obstacle_at_next) and self.active_powerup != "shield":
            self.finish_game()
            return
        if (next_head in body_to_check or obstacle_at_next) and self.active_powerup == "shield":
            shield_blocked = True

        self.snake.insert(0, next_head)

        food = self.food_at(next_head)
        if food is not None:
            self.foods = [item for item in self.foods if item.cell != next_head]
            if food.kind == "poison":
                self.message = "Poison food!"
                for _ in range(2):
                    if len(self.snake) > 1:
                        self.snake.pop()
                if len(self.snake) <= 1:
                    self.finish_game()
                    return
            else:
                self.score += food.points
            self.update_level()
            while len(self.foods) < TARGET_FOOD_COUNT:
                self.spawn_food()

        if self.powerup is not None and self.powerup.cell == next_head:
            self.collect_powerup(self.powerup)

        if not will_eat:
            self.snake.pop()

        if shield_blocked:
            self.active_powerup = ""
            self.active_powerup_until = 0
            self.message = "Shield blocked the collision."

    def cell_to_screen(self, cell: Point) -> tuple[int, int]:
        return BOARD_LEFT + cell[0] * CELL_SIZE, BOARD_TOP + cell[1] * CELL_SIZE

    def run(self, max_frames: int = 0) -> None:
        self.max_frames = max_frames
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            self.handle_events()
            self.update(dt)
            self.draw()
            self.frames += 1
            if self.max_frames and self.frames >= self.max_frames:
                self.running = False
        pygame.quit()


def parse_args(argv: Iterable[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Practice 11 Snake")
    parser.add_argument("--headless", action="store_true", help="Run without opening a real window")
    parser.add_argument("--max-frames", type=int, default=0, help="Stop after N frames")
    return parser.parse_args(list(argv))


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    game = SnakeGame(headless=args.headless)
    game.run(max_frames=args.max_frames)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
