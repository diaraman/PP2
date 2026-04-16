import pygame
from datetime import datetime

class MickeyClock:
    def __init__(self, screen):
        # Save screen and clock center position
        self.screen=screen
        self.center=(300, 300)

        # Load and resize background image
        self.bg=pygame.image.load("mickeys_clock/images/clock_bg.png").convert()
        self.bg=pygame.transform.scale(self.bg, (600, 600))

        # Load and resize hand image (used for both minute/second hands)
        self.hand=pygame.image.load("mickeys_clock/images/mickey_hand.png").convert_alpha()
        self.hand=pygame.transform.scale(self.hand, (260, 260))

    def get_time(self):
            # Get current system time
            now=datetime.now()
            # Return only minute and second
            return now.minute, now.second
    
    def rotate(self, image, angle):
            # Rotate hand image and keep its center at clock center
            rotated_image=pygame.transform.rotate(image, angle)
            rect=rotated_image.get_rect(center=self.center)
            return rotated_image, rect
    
    def draw(self):
            # 1) Calculate hand angles from current time
            minutes, seconds=self.get_time()
            min_angle=-(minutes*6+seconds*0.1)
            sec_angle=-seconds*6

            # 2) Draw background
            self.screen.blit(self.bg, (0, 0))

            # 3) Rotate minute and second hands
            min_hand, min_rect=self.rotate(self.hand, min_angle)
            sec_hand, sec_rect=self.rotate(self.hand, sec_angle)

            # 4) Draw hands
            self.screen.blit(min_hand, min_rect)
            self.screen.blit(sec_hand, sec_rect)
