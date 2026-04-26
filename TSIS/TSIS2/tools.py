from __future__ import annotations

from collections import deque
from datetime import datetime
from pathlib import Path

import pygame


CANVAS_BG = (255, 255, 255)

PALETTE = [
    (20, 20, 20),
    (255, 255, 255),
    (220, 50, 50),
    (50, 95, 220),
    (45, 165, 70),
    (245, 180, 40),
    (155, 80, 210),
    (35, 180, 190),
    (235, 125, 40),
    (120, 120, 120),
    (95, 55, 35),
    (255, 105, 180),
]

BRUSH_SIZES = {
    1: 2,
    2: 5,
    3: 10,
}


def draw_button(screen: pygame.Surface, rect: pygame.Rect, label: str, font: pygame.font.Font, selected: bool = False) -> None:
    fill = (185, 211, 242) if selected else (216, 222, 232)
    border = (72, 96, 140) if selected else (116, 124, 138)
    pygame.draw.rect(screen, fill, rect, border_radius=8)
    pygame.draw.rect(screen, border, rect, width=2, border_radius=8)
    text = font.render(label, True, (20, 24, 30))
    screen.blit(text, text.get_rect(center=rect.center))


def clamp_point(pos: tuple[int, int], width: int, height: int) -> tuple[int, int]:
    x = max(0, min(width - 1, pos[0]))
    y = max(0, min(height - 1, pos[1]))
    return x, y


def flood_fill(surface: pygame.Surface, start_pos: tuple[int, int], new_color: tuple[int, int, int]) -> None:
    width, height = surface.get_size()
    x, y = start_pos
    if not (0 <= x < width and 0 <= y < height):
        return

    target = surface.get_at((x, y))
    replacement = pygame.Color(*new_color)
    if target == replacement:
        return

    queue: deque[tuple[int, int]] = deque([(x, y)])
    while queue:
        px, py = queue.pop()
        if not (0 <= px < width and 0 <= py < height):
            continue
        if surface.get_at((px, py)) != target:
            continue

        surface.set_at((px, py), replacement)
        queue.append((px + 1, py))
        queue.append((px - 1, py))
        queue.append((px, py + 1))
        queue.append((px, py - 1))


def save_canvas(surface: pygame.Surface, folder: Path | str = ".") -> Path:
    folder_path = Path(folder)
    folder_path.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    filename = folder_path / f"canvas_{timestamp}.png"
    pygame.image.save(surface, str(filename))
    return filename
