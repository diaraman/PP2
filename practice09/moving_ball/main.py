import pygame
import sys

from ball import Ball


# Start pygame modules
pygame.init()

# Window settings
WIDTH = 800
HEIGHT = 600
WHITE = (255, 255, 255)

# Create game window
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Moving Ball Game")

# Create ball object and FPS timer
ball = Ball(WIDTH, HEIGHT)
clock = pygame.time.Clock()
# Delay between repeated moves while key is held
move_delay_ms = 80
last_move_time = 0

# Main game loop
while True:
    # 1) Read events (close window, single key press movement)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                ball.move_left()
            elif event.key == pygame.K_RIGHT:
                ball.move_right()
            elif event.key == pygame.K_UP:
                ball.move_up()
            elif event.key == pygame.K_DOWN:
                ball.move_down()

    # 2) Continuous movement while key is held down
    now = pygame.time.get_ticks()
    if now - last_move_time >= move_delay_ms:
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            ball.move_left()
            last_move_time = now
        elif keys[pygame.K_RIGHT]:
            ball.move_right()
            last_move_time = now
        elif keys[pygame.K_UP]:
            ball.move_up()
            last_move_time = now
        elif keys[pygame.K_DOWN]:
            ball.move_down()
            last_move_time = now

    # 3) Draw frame
    screen.fill(WHITE)
    ball.draw(screen)

    pygame.display.flip()
    # Keep animation smooth
    clock.tick(60)
