import pygame
import sys
from player import MusicPlayer

# Initialize pygame core modules (window, events, time, etc.)
pygame.init()
# Initialize mixer module (audio playback)
pygame.mixer.init()

# Create application window
screen = pygame.display.set_mode((760, 420))
pygame.display.set_caption("Keyboard Music Player")

# Create music player object and FPS timer
player = MusicPlayer(screen)
clock = pygame.time.Clock()

# Temporary UI message (for example after pressing R)
message = ""
message_until = 0

# Main app loop
while True:
    # 1) Handle events (quit + keyboard controls)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                pygame.quit()
                sys.exit()
            elif event.key == pygame.K_p:
                player.play()
            elif event.key == pygame.K_s:
                player.stop()
            elif event.key == pygame.K_n:
                player.next_track()
            elif event.key == pygame.K_b:
                player.previous_track()
            elif event.key == pygame.K_r:
                player.reload_playlist()
                message = f"Reloaded: {len(player.playlist)} track(s)"
                message_until = pygame.time.get_ticks() + 1500

    # 2) If current song ended, switch to next automatically
    player.update_auto_next()

    # 3) Hide temporary message after 1.5 seconds
    if pygame.time.get_ticks() > message_until:
        message = ""

    # 4) Draw UI and update screen
    player.draw(message)
    pygame.display.flip()
    # Keep loop speed stable
    clock.tick(30)
