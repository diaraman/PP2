import random
from pathlib import Path
import pygame


SCREEN_W = 500
SCREEN_H = 600
ROAD_LEFT = 50
ROAD_RIGHT = SCREEN_W - 50
IMG_DIR = Path(__file__).resolve().parent / "img"


def load_image(name, size, fallback_color):
    image_path = IMG_DIR / name
    if image_path.exists():
        image = pygame.image.load(str(image_path)).convert_alpha()
        return pygame.transform.smoothscale(image, size)

    surface = pygame.Surface(size, pygame.SRCALPHA)
    surface.fill(fallback_color)
    return surface


class Player(pygame.sprite.Sprite):
    def __init__(self, x_pos, y_pos):
        super().__init__()
        self.image = load_image("red_car.png", (50, 80), (220, 30, 30))
        self.rect = self.image.get_rect(center=(x_pos, y_pos))

    def check_collisions(self, objects):
        return pygame.sprite.spritecollide(self, objects, False)

    def check_collisions_coin(self, coin_group):
        return pygame.sprite.spritecollide(self, coin_group, True)


class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = load_image("blue_car.png", (50, 80), (30, 100, 220))
        self.rect = self.image.get_rect(center=(random.randint(100, 400), 0))

    def update(self):
        self.rect.y += 6


class Coin(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((40, 40), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (240, 200, 40), (20, 20), 18)
        pygame.draw.circle(self.image, (25, 25, 25), (20, 20), 18, 2)
        self.rect = self.image.get_rect(center=(random.randint(100, 400), 0))

    def update(self):
        self.rect.y += 5
