from __future__ import annotations

import math
import sys
from pathlib import Path

import pygame

from tools import BRUSH_SIZES, CANVAS_BG, PALETTE, clamp_point, draw_button, flood_fill, save_canvas


pygame.init()

SCREEN_W = 1320
SCREEN_H = 840
TOP_BAR_H = 88
SIDE_BAR_W = 260
CANVAS_X = SIDE_BAR_W + 14
CANVAS_Y = TOP_BAR_H + 14
CANVAS_W = SCREEN_W - CANVAS_X - 14
CANVAS_H = SCREEN_H - CANVAS_Y - 14

screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("Paint Extended")
clock = pygame.time.Clock()

font = pygame.font.Font(None, 30)
small_font = pygame.font.Font(None, 22)
tiny_font = pygame.font.Font(None, 18)

canvas = pygame.Surface((CANVAS_W, CANVAS_H))
canvas.fill(CANVAS_BG)

tools = ["pencil", "line", "rect", "circle", "fill", "text", "eraser"]
tool_shortcuts = {
    pygame.K_p: "pencil",
    pygame.K_l: "line",
    pygame.K_r: "rect",
    pygame.K_o: "circle",
    pygame.K_f: "fill",
    pygame.K_t: "text",
    pygame.K_e: "eraser",
}

active_tool = "pencil"
active_size = BRUSH_SIZES[1]
active_color = (20, 20, 20)

drawing = False
last_pos: tuple[int, int] | None = None
start_pos: tuple[int, int] | None = None
preview_pos: tuple[int, int] | None = None
text_mode = False
text_input = ""
text_pos = (0, 0)

tool_buttons: dict[str, pygame.Rect] = {}
size_buttons: dict[int, pygame.Rect] = {}
color_buttons: list[tuple[pygame.Rect, tuple[int, int, int]]] = []
clear_button: pygame.Rect | None = None
save_button: pygame.Rect | None = None


def canvas_rect() -> pygame.Rect:
    return pygame.Rect(CANVAS_X, CANVAS_Y, CANVAS_W, CANVAS_H)


def canvas_to_screen(pos: tuple[int, int]) -> tuple[int, int]:
    return pos[0] + CANVAS_X, pos[1] + CANVAS_Y


def in_canvas(pos: tuple[int, int]) -> bool:
    return canvas_rect().collidepoint(pos)


def to_canvas_pos(pos: tuple[int, int]) -> tuple[int, int]:
    return clamp_point((pos[0] - CANVAS_X, pos[1] - CANVAS_Y), CANVAS_W, CANVAS_H)


def draw_top_bar() -> None:
    pygame.draw.rect(screen, (214, 221, 232), (0, 0, SCREEN_W, TOP_BAR_H))
    pygame.draw.line(screen, (142, 150, 164), (0, TOP_BAR_H), (SCREEN_W, TOP_BAR_H), 2)

    title = font.render("Paint Extended", True, (34, 42, 55))
    screen.blit(title, (16, 10))
    hint_1 = tiny_font.render("P pencil  L line  R rectangle  O circle  F fill  T text  E eraser", True, (62, 69, 82))
    hint_2 = tiny_font.render("1/2/3 size  Ctrl+S save  C clear canvas  Esc quit", True, (62, 69, 82))
    screen.blit(hint_1, (16, 42))
    screen.blit(hint_2, (16, 60))


def draw_sidebar() -> None:
    global tool_buttons, size_buttons, color_buttons, clear_button, save_button

    pygame.draw.rect(screen, (224, 229, 238), (0, TOP_BAR_H, SIDE_BAR_W, SCREEN_H - TOP_BAR_H))
    pygame.draw.line(screen, (142, 150, 164), (SIDE_BAR_W, TOP_BAR_H), (SIDE_BAR_W, SCREEN_H), 2)

    y = TOP_BAR_H + 14
    tool_buttons = {}
    screen.blit(small_font.render("Tools", True, (40, 48, 64)), (16, y))
    y += 28
    tool_grid = [("pencil", 0, 0), ("line", 1, 0), ("rect", 0, 1), ("circle", 1, 1), ("fill", 0, 2), ("text", 1, 2), ("eraser", 0, 3)]
    for name, col, row in tool_grid:
        rect = pygame.Rect(16 + col * 104, y + row * 40, 96, 32)
        tool_buttons[name] = rect
        draw_button(screen, rect, name.title(), small_font, active_tool == name)

    y = TOP_BAR_H + 210
    screen.blit(small_font.render("Brush size", True, (40, 48, 64)), (16, y))
    size_buttons = {}
    for idx, level in enumerate((1, 2, 3)):
        rect = pygame.Rect(16, y + 26 + idx * 40, 64, 32)
        size_buttons[level] = rect
        draw_button(screen, rect, str(BRUSH_SIZES[level]), small_font, active_size == BRUSH_SIZES[level])
        pygame.draw.circle(screen, (20, 20, 20), (118, y + 42 + idx * 40), max(2, BRUSH_SIZES[level] // 2))

    y = TOP_BAR_H + 360
    screen.blit(small_font.render("Colors", True, (40, 48, 64)), (16, y))
    color_buttons = []
    cols = 3
    for idx, color in enumerate(PALETTE):
        row = idx // cols
        col = idx % cols
        rect = pygame.Rect(16 + col * 44, y + 26 + row * 42, 32, 32)
        pygame.draw.rect(screen, color, rect, border_radius=6)
        border = (20, 20, 20) if color == active_color else (120, 126, 138)
        pygame.draw.rect(screen, border, rect, width=2, border_radius=6)
        color_buttons.append((rect, color))

    preview = pygame.Rect(16, SCREEN_H - 168, 226, 42)
    pygame.draw.rect(screen, (248, 248, 250), preview, border_radius=8)
    pygame.draw.rect(screen, (120, 126, 138), preview, width=1, border_radius=8)
    pygame.draw.rect(screen, active_color, pygame.Rect(preview.x + 12, preview.y + 9, 24, 24), border_radius=5)
    label = tiny_font.render(f"{active_tool} | size {active_size}", True, (40, 48, 64))
    screen.blit(label, (preview.x + 46, preview.y + 13))

    clear_button = pygame.Rect(16, SCREEN_H - 106, 226, 34)
    save_button = pygame.Rect(16, SCREEN_H - 62, 226, 34)
    draw_button(screen, clear_button, "Clear Canvas", small_font)
    draw_button(screen, save_button, "Save PNG", small_font)


def draw_canvas_frame() -> None:
    rect = canvas_rect()
    pygame.draw.rect(screen, (178, 186, 202), rect.inflate(8, 8), border_radius=4)
    screen.blit(canvas, (CANVAS_X, CANVAS_Y))
    pygame.draw.rect(screen, (82, 88, 101), rect, width=2)


def draw_preview() -> None:
    if drawing and start_pos and preview_pos:
        if active_tool == "line":
            pygame.draw.line(screen, active_color, canvas_to_screen(start_pos), canvas_to_screen(preview_pos), active_size)
        elif active_tool == "rect":
            x1, y1 = start_pos
            x2, y2 = preview_pos
            rect = pygame.Rect(
                CANVAS_X + min(x1, x2),
                CANVAS_Y + min(y1, y2),
                abs(x2 - x1),
                abs(y2 - y1),
            )
            pygame.draw.rect(screen, active_color, rect, width=active_size)
        elif active_tool == "circle":
            radius = int(math.dist(start_pos, preview_pos))
            pygame.draw.circle(screen, active_color, canvas_to_screen(start_pos), max(1, radius), active_size)

    if text_mode:
        blink = pygame.time.get_ticks() % 1000 < 500
        rendered = font.render(text_input or ("|" if blink else ""), True, active_color)
        screen.blit(rendered, canvas_to_screen(text_pos))


def start_shape(pos: tuple[int, int]) -> None:
    global drawing, last_pos, start_pos, preview_pos
    drawing = True
    last_pos = pos
    start_pos = pos
    preview_pos = pos


def end_shape(pos: tuple[int, int]) -> None:
    global drawing, last_pos, start_pos, preview_pos
    if not start_pos:
        drawing = False
        return

    if active_tool == "line":
        pygame.draw.line(canvas, active_color, start_pos, pos, active_size)
    elif active_tool == "rect":
        x1, y1 = start_pos
        x2, y2 = pos
        rect = pygame.Rect(min(x1, x2), min(y1, y2), abs(x2 - x1), abs(y2 - y1))
        pygame.draw.rect(canvas, active_color, rect, width=active_size)
    elif active_tool == "circle":
        radius = int(math.dist(start_pos, pos))
        pygame.draw.circle(canvas, active_color, start_pos, max(1, radius), active_size)

    drawing = False
    last_pos = None
    start_pos = None
    preview_pos = None


def handle_text_key(event: pygame.event.Event) -> None:
    global text_mode, text_input
    if event.key == pygame.K_ESCAPE:
        text_mode = False
        text_input = ""
        return
    if event.key == pygame.K_RETURN:
        if text_input:
            rendered = font.render(text_input, True, active_color)
            canvas.blit(rendered, text_pos)
        text_mode = False
        text_input = ""
        return
    if event.key == pygame.K_BACKSPACE:
        text_input = text_input[:-1]
        return

    if event.unicode and event.unicode.isprintable():
        text_input += event.unicode


def handle_keydown(event: pygame.event.Event) -> None:
    global active_tool, active_size, active_color, text_mode, text_input

    if event.mod & pygame.KMOD_CTRL and event.key == pygame.K_s:
        path = save_canvas(canvas, Path("."))
        print(f"Saved: {path}")
        return

    if event.key in (pygame.K_1, pygame.K_2, pygame.K_3):
        active_size = BRUSH_SIZES[int(chr(event.key))]
        return

    if text_mode:
        handle_text_key(event)
        return

    if event.key in tool_shortcuts:
        active_tool = tool_shortcuts[event.key]
    elif event.key == pygame.K_ESCAPE:
        pygame.quit()
        sys.exit()
    elif event.key == pygame.K_c:
        canvas.fill(CANVAS_BG)


def handle_mouse_down(event: pygame.event.Event) -> None:
    global active_tool, active_size, active_color, text_mode, text_input, text_pos

    pos = event.pos
    if clear_button and clear_button.collidepoint(pos):
        canvas.fill(CANVAS_BG)
        return
    if save_button and save_button.collidepoint(pos):
        path = save_canvas(canvas, Path("."))
        print(f"Saved: {path}")
        return

    for name, rect in tool_buttons.items():
        if rect.collidepoint(pos):
            active_tool = name
            return

    for level, rect in size_buttons.items():
        if rect.collidepoint(pos):
            active_size = BRUSH_SIZES[level]
            return

    for rect, color in color_buttons:
        if rect.collidepoint(pos):
            active_color = color
            return

    if not in_canvas(pos):
        return

    local = to_canvas_pos(pos)
    if active_tool == "fill":
        flood_fill(canvas, local, active_color)
    elif active_tool == "text":
        text_mode = True
        text_input = ""
        text_pos = local
    else:
        start_shape(local)


def handle_mouse_up(event: pygame.event.Event) -> None:
    if not drawing or not start_pos:
        return

    local = to_canvas_pos(event.pos) if in_canvas(event.pos) else preview_pos or start_pos
    if active_tool in {"line", "rect", "circle"}:
        end_shape(local)
    else:
        end_shape(local)


def handle_mouse_motion(event: pygame.event.Event) -> None:
    global last_pos, preview_pos

    if not drawing or not in_canvas(event.pos):
        return

    local = to_canvas_pos(event.pos)
    if active_tool in {"pencil", "eraser"} and last_pos is not None:
        draw_color = CANVAS_BG if active_tool == "eraser" else active_color
        pygame.draw.line(canvas, draw_color, last_pos, local, active_size)
        pygame.draw.circle(canvas, draw_color, local, max(1, active_size // 2))
        last_pos = local
    elif active_tool in {"line", "rect", "circle"}:
        preview_pos = local


def main() -> None:
    global drawing, text_mode

    while True:
        screen.fill((228, 232, 240))
        draw_top_bar()
        draw_sidebar()
        draw_canvas_frame()
        draw_preview()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                handle_keydown(event)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                handle_mouse_down(event)
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                handle_mouse_up(event)
            elif event.type == pygame.MOUSEMOTION:
                handle_mouse_motion(event)

        pygame.display.flip()
        clock.tick(120)


if __name__ == "__main__":
    main()
