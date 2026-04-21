import random
import sys
import pygame

from race import Player, Enemy, Coin, SCREEN_W, SCREEN_H, ROAD_LEFT, ROAD_RIGHT


pygame.init()
pygame.display.set_caption("Racer")

screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
clock = pygame.time.Clock()

hud_font = pygame.font.Font(None, 42)
small_font = pygame.font.Font(None, 30)

player_group = pygame.sprite.GroupSingle(Player())
enemy_group = pygame.sprite.Group()
coin_group = pygame.sprite.Group()

score = 0
coins_collected = 0
running = True

SPAWN_ENEMY = pygame.USEREVENT + 1
SPAWN_COIN = pygame.USEREVENT + 2
pygame.time.set_timer(SPAWN_ENEMY, 1200)
pygame.time.set_timer(SPAWN_COIN, random.randint(1200, 2600))

road_offset = 0


def draw_road(surface, offset):
    """Draw grass, road, and moving lane separators."""
    surface.fill((26, 135, 26))
    pygame.draw.rect(surface, (55, 55, 55), (ROAD_LEFT, 0, ROAD_RIGHT - ROAD_LEFT, SCREEN_H))
    pygame.draw.line(surface, (245, 245, 245), (ROAD_LEFT, 0), (ROAD_LEFT, SCREEN_H), 4)
    pygame.draw.line(surface, (245, 245, 245), (ROAD_RIGHT, 0), (ROAD_RIGHT, SCREEN_H), 4)

    lane1_x = ROAD_LEFT + (ROAD_RIGHT - ROAD_LEFT) // 3
    lane2_x = ROAD_LEFT + 2 * (ROAD_RIGHT - ROAD_LEFT) // 3
    dash_h = 80
    gap = 45
    y = -dash_h + offset
    while y < SCREEN_H:
        pygame.draw.rect(surface, (240, 240, 120), (lane1_x - 4, y, 8, dash_h))
        pygame.draw.rect(surface, (240, 240, 120), (lane2_x - 4, y, 8, dash_h))
        y += dash_h + gap


def draw_hud(surface, score_value, coin_value):
    """Draw top HUD with score and collected coin count."""
    pygame.draw.rect(surface, (15, 15, 18), (0, 0, SCREEN_W, 54))
    score_surf = hud_font.render(f"Score: {score_value}", True, (255, 255, 255))
    surface.blit(score_surf, (14, 8))

    coin_surf = hud_font.render(f"Coins: {coin_value}", True, (255, 225, 80))
    coin_rect = coin_surf.get_rect(topright=(SCREEN_W - 14, 8))
    surface.blit(coin_surf, coin_rect)


while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == SPAWN_ENEMY:
            enemy_speed = 7 + min(score // 8, 6)
            enemy_group.add(Enemy(enemy_speed))

        if event.type == SPAWN_COIN:
            coin_group.add(Coin())
            pygame.time.set_timer(SPAWN_COIN, random.randint(1200, 2600))

    keys = pygame.key.get_pressed()
    player_group.sprite.move(keys)

    enemy_group.update()
    coin_group.update()
    road_offset = (road_offset + 10) % 125

    if pygame.sprite.spritecollide(player_group.sprite, enemy_group, False):
        running = False

    got_coins = pygame.sprite.spritecollide(player_group.sprite, coin_group, True)
    if got_coins:
        coins_collected += len(got_coins)
        score += len(got_coins)

    score += 1 / 60

    draw_road(screen, road_offset)
    enemy_group.draw(screen)
    coin_group.draw(screen)
    player_group.draw(screen)
    draw_hud(screen, int(score), coins_collected)

    hint = small_font.render("Move: A/D or Left/Right", True, (230, 230, 230))
    screen.blit(hint, (12, SCREEN_H - 30))

    pygame.display.update()
    clock.tick(60)

after_font = pygame.font.Font(None, 56)
end_text = after_font.render("Game Over", True, (255, 255, 255))
end_rect = end_text.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2 - 20))
sub_text = small_font.render("Press ESC or close window", True, (230, 230, 230))
sub_rect = sub_text.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2 + 30))

waiting = True
while waiting:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            waiting = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            waiting = False

    screen.fill((20, 20, 24))
    screen.blit(end_text, end_rect)
    screen.blit(sub_text, sub_rect)
    pygame.display.update()
    clock.tick(30)

pygame.quit()
sys.exit()
