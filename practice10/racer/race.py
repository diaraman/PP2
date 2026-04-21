import random
from pathlib import Path
import pygame


SCREEN_W = 500
SCREEN_H = 900
ROAD_LEFT = 75
ROAD_RIGHT = 425
LANES_X = [140, 250, 360]

IMG_DIR = Path(__file__).resolve().parent / "img"


def load_scaled_image(name, size, fallback_color):
    """Load image from img folder. If missing, use colored rectangle fallback."""
    image_path = IMG_DIR / name
    if image_path.exists():
        image = pygame.image.load(str(image_path)).convert_alpha()
        return pygame.transform.smoothscale(image, size)

    surf = pygame.Surface(size, pygame.SRCALPHA)
    surf.fill(fallback_color)
    return surf


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
