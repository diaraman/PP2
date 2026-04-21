import sys
import pygame

pygame.init()
pygame.display.set_caption("Paint (Simple UI)")

SCREEN_W = 980
SCREEN_H = 720
TOP_BAR_H = 82
SIDE_BAR_W = 190
CANVAS_X = SIDE_BAR_W + 12
CANVAS_Y = TOP_BAR_H + 12
CANVAS_W = SCREEN_W - CANVAS_X - 12
CANVAS_H = SCREEN_H - CANVAS_Y - 12
CANVAS_BG = (252, 252, 252)

screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
clock = pygame.time.Clock()
font = pygame.font.Font(None, 26)
small_font = pygame.font.Font(None, 22)

canvas = pygame.Surface((CANVAS_W, CANVAS_H))
canvas.fill(CANVAS_BG)

active_tool = "brush"
active_size = 8
active_color = (30, 30, 30)
drawing = False
last_pos = None
rect_start = None
preview_pos = None

palette = [
    (30, 30, 30), (255, 255, 255), (220, 40, 40), (50, 90, 220),
    (40, 160, 60), (245, 185, 35), (155, 80, 210), (35, 180, 190),
    (235, 125, 40), (120, 120, 120), (95, 55, 35), (255, 105, 180),
]
size_values = [4, 8, 14, 22]

tool_buttons = {}
size_buttons = {}
color_buttons = []
clear_button = None


def draw_button(rect, label, selected=False):
    color = (210, 216, 226) if not selected else (162, 194, 235)
    pygame.draw.rect(screen, color, rect, border_radius=8)
    pygame.draw.rect(screen, (110, 120, 136), rect, width=2, border_radius=8)
    text = small_font.render(label, True, (20, 24, 30))
    screen.blit(text, text.get_rect(center=rect.center))


def draw_ui():
    global tool_buttons, size_buttons, color_buttons, clear_button

    screen.fill((224, 229, 238))
    pygame.draw.rect(screen, (209, 219, 231), (0, 0, SCREEN_W, TOP_BAR_H))
    pygame.draw.line(screen, (145, 152, 165), (0, TOP_BAR_H), (SCREEN_W, TOP_BAR_H), 2)

    title = font.render("Paint - simple and clean", True, (34, 42, 55))
    screen.blit(title, (16, 12))
    hint = small_font.render("Tools on left | Draw on white area | C = clear canvas", True, (60, 68, 82))
    screen.blit(hint, (16, 44))

    pygame.draw.rect(screen, (213, 219, 231), (0, TOP_BAR_H, SIDE_BAR_W, SCREEN_H - TOP_BAR_H))
    pygame.draw.line(screen, (145, 152, 165), (SIDE_BAR_W, TOP_BAR_H), (SIDE_BAR_W, SCREEN_H), 2)

    y = TOP_BAR_H + 16
    tool_buttons = {
        "brush": pygame.Rect(16, y, 158, 36),
        "rect": pygame.Rect(16, y + 44, 158, 36),
        "eraser": pygame.Rect(16, y + 88, 158, 36),
    }
    draw_button(tool_buttons["brush"], "Brush", active_tool == "brush")
    draw_button(tool_buttons["rect"], "Rectangle", active_tool == "rect")
    draw_button(tool_buttons["eraser"], "Eraser", active_tool == "eraser")

    size_label = small_font.render("Brush size", True, (40, 48, 64))
    screen.blit(size_label, (16, y + 140))

    size_buttons = {}
    sy = y + 166
    for value in size_values:
        rect = pygame.Rect(16, sy, 74, 34)
        size_buttons[value] = rect
        draw_button(rect, str(value), active_size == value)
        preview_x = 120
        pygame.draw.circle(screen, (30, 30, 30), (preview_x, sy + 17), max(2, value // 2))
        sy += 40

    color_label = small_font.render("Colors", True, (40, 48, 64))
    screen.blit(color_label, (16, sy + 8))
    sy += 34

    color_buttons = []
    for idx, color in enumerate(palette):
        col = idx % 2
        row = idx // 2
        rect = pygame.Rect(16 + col * 44, sy + row * 40, 34, 34)
        pygame.draw.rect(screen, color, rect, border_radius=5)
        border = (20, 20, 20) if color == active_color else (120, 126, 138)
        pygame.draw.rect(screen, border, rect, width=2, border_radius=5)
        color_buttons.append((rect, color))

    clear_button = pygame.Rect(16, SCREEN_H - 54, 158, 36)
    draw_button(clear_button, "Clear Canvas", False)

    canvas_rect = pygame.Rect(CANVAS_X, CANVAS_Y, CANVAS_W, CANVAS_H)
    pygame.draw.rect(screen, (178, 186, 202), canvas_rect.inflate(4, 4), border_radius=2)
    screen.blit(canvas, (CANVAS_X, CANVAS_Y))

    return canvas_rect


def in_canvas(pos, canvas_rect):
    return canvas_rect.collidepoint(pos)


def canvas_pos(mouse_pos):
    return mouse_pos[0] - CANVAS_X, mouse_pos[1] - CANVAS_Y


while True:
    canvas_rect = draw_ui()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN and event.key == pygame.K_c:
            canvas.fill(CANVAS_BG)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos

            if clear_button and clear_button.collidepoint(pos):
                canvas.fill(CANVAS_BG)
                continue

            for name, rect in tool_buttons.items():
                if rect.collidepoint(pos):
                    active_tool = name
                    break

            for value, rect in size_buttons.items():
                if rect.collidepoint(pos):
                    active_size = value
                    break

            for rect, color in color_buttons:
                if rect.collidepoint(pos):
                    active_color = color
                    break

            if in_canvas(pos, canvas_rect):
                drawing = True
                local_pos = canvas_pos(pos)
                last_pos = local_pos
                if active_tool == "rect":
                    rect_start = local_pos
                    preview_pos = local_pos

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if drawing and active_tool == "rect" and rect_start and preview_pos:
                x1, y1 = rect_start
                x2, y2 = preview_pos
                rect = pygame.Rect(min(x1, x2), min(y1, y2), abs(x2 - x1), abs(y2 - y1))
                pygame.draw.rect(canvas, active_color, rect, width=0)
            drawing = False
            last_pos = None
            rect_start = None
            preview_pos = None

        if event.type == pygame.MOUSEMOTION and drawing:
            if not in_canvas(event.pos, canvas_rect):
                continue
            local_pos = canvas_pos(event.pos)
            if active_tool in ("brush", "eraser") and last_pos:
                color = CANVAS_BG if active_tool == "eraser" else active_color
                pygame.draw.line(canvas, color, last_pos, local_pos, active_size * 2)
                pygame.draw.circle(canvas, color, local_pos, active_size)
                last_pos = local_pos
            elif active_tool == "rect":
                preview_pos = local_pos

    if drawing and active_tool == "rect" and rect_start and preview_pos:
        x1, y1 = rect_start
        x2, y2 = preview_pos
        preview_rect = pygame.Rect(
            CANVAS_X + min(x1, x2),
            CANVAS_Y + min(y1, y2),
            abs(x2 - x1),
            abs(y2 - y1),
        )
        pygame.draw.rect(screen, active_color, preview_rect, width=2)

    pygame.display.update()
    clock.tick(120)
