import pygame
import sys
from clock import MickeyClock

# Start pygame
pygame.init()
# Create 600x600 window
screen=pygame.display.set_mode((600, 600))
pygame.display.set_caption("Mickey Clock")

# Create clock object and FPS controller
mickey=MickeyClock(screen)
clock=pygame.time.Clock()

# Main loop: events -> draw -> update screen
while True:
    for event in pygame.event.get():
        if event.type==pygame.QUIT:
            pygame.quit()
            sys.exit()

    mickey.draw()
    pygame.display.flip()
    clock.tick(60)
