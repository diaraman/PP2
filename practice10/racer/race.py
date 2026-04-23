import random
from pathlib import Path
import pygame


SCREEN_W = 500
SCREEN_H = 900
ROAD_LEFT = 75
ROAD_RIGHT = 425
LANES_X = [140, 250, 360]

IMG_DIR = Path(__file__).resolve().parent / "img"


def build_car_sprite(base_color, accent_color, size):
    """Create a simple car sprite as a PNG when no asset file exists."""
    surface = pygame.Surface(size, pygame.SRCALPHA)
    w, h = size

    body = pygame.Rect(w * 0.18, h * 0.28, w * 0.64, h * 0.52)
    roof = pygame.Rect(w * 0.30, h * 0.10, w * 0.40, h * 0.28)
    windshield = pygame.Rect(w * 0.34, h * 0.15, w * 0.32, h * 0.14)
    bumper_top = pygame.Rect(w * 0.24, h * 0.72, w * 0.52, h * 0.08)

    pygame.draw.rect(surface, base_color, body, border_radius=12)
    pygame.draw.rect(surface, base_color, roof, border_radius=10)
    pygame.draw.rect(surface, accent_color, windshield, border_radius=8)
    pygame.draw.rect(surface, (25, 25, 25), bumper_top, border_radius=6)

    wheel_y = int(h * 0.70)
    wheel_r = max(6, int(min(w, h) * 0.10))
    for wheel_x in (int(w * 0.24), int(w * 0.72)):
        pygame.draw.circle(surface, (20, 20, 20), (wheel_x, wheel_y), wheel_r)
        pygame.draw.circle(surface, (90, 90, 90), (wheel_x, wheel_y), max(2, wheel_r // 2))

    pygame.draw.rect(surface, (255, 255, 255), (w * 0.28, h * 0.45, w * 0.16, h * 0.07), border_radius=3)
    pygame.draw.rect(surface, (255, 255, 255), (w * 0.56, h * 0.45, w * 0.16, h * 0.07), border_radius=3)

    return surface


def ensure_asset_file(name, surface):
    """Save a generated asset the first time the game runs."""
    image_path = IMG_DIR / name
    IMG_DIR.mkdir(parents=True, exist_ok=True)
    if not image_path.exists():
        pygame.image.save(surface, str(image_path))


def load_scaled_image(name, size, fallback_color):
    """Load image from img folder. If missing, generate a simple car PNG."""
    image_path = IMG_DIR / name
    if image_path.exists():
        image = pygame.image.load(str(image_path)).convert_alpha()
        return pygame.transform.smoothscale(image, size)

    if name == "pngegg.png":
        generated = build_car_sprite((220, 40, 40), (255, 210, 210), size)
    elif name == "blue_car.png":
        generated = build_car_sprite((50, 90, 220), (210, 225, 255), size)
    else:
        generated = pygame.Surface(size, pygame.SRCALPHA)
        generated.fill(fallback_color)

    ensure_asset_file(name, generated)
    return generated


class Player(pygame.sprite.Sprite):
    """Player car controlled with keyboard."""

    def __init__(self):
        super().__init__()
        self.image = load_scaled_image("pngegg.png", (90, 140), (255, 100, 100))
        self.rect = self.image.get_rect(midbottom=(LANES_X[1], SCREEN_H - 30))
        self.speed = 7

    def move(self, keys):
        """Handle smooth horizontal movement and keep car on the road."""
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.rect.x += self.speed

        if self.rect.left < ROAD_LEFT + 8:
            self.rect.left = ROAD_LEFT + 8
        if self.rect.right > ROAD_RIGHT - 8:
            self.rect.right = ROAD_RIGHT - 8


class Enemy(pygame.sprite.Sprite):
    """Enemy car that spawns at top and moves downward."""

    def __init__(self, speed=7):
        super().__init__()
        self.image = load_scaled_image("blue_car.png", (90, 140), (40, 160, 255))
        lane_x = random.choice(LANES_X)
        self.rect = self.image.get_rect(midtop=(lane_x, -150))
        self.speed = speed

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > SCREEN_H + 20:
            self.kill()


class Coin(pygame.sprite.Sprite):
    """Collectible coin that appears randomly on the road."""

    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((38, 38), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (255, 214, 60), (19, 19), 17)
        pygame.draw.circle(self.image, (255, 238, 130), (19, 19), 11)
        lane_x = random.choice(LANES_X)
        y = random.randint(-450, -50)
        self.rect = self.image.get_rect(center=(lane_x, y))
        self.speed = 6

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > SCREEN_H + 10:
            self.kill()
