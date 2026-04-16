import pygame


class Ball:
    def __init__(self, screen_width, screen_height):
        # Ball is 50x50 in diameter -> radius 25
        self.radius = 25
        self.color = (255, 0, 0)
        # Ball moves 20 pixels per action
        self.step = 20

        # Save screen size for boundary checks
        self.screen_width = screen_width
        self.screen_height = screen_height

        # Start from screen center
        self.x = screen_width // 2
        self.y = screen_height // 2

    def move_left(self):
        # Try to move left; apply only if ball stays inside window
        new_x = self.x - self.step
        if new_x - self.radius >= 0:
            self.x = new_x

    def move_right(self):
        # Try to move right; apply only if ball stays inside window
        new_x = self.x + self.step
        if new_x + self.radius <= self.screen_width:
            self.x = new_x

    def move_up(self):
        # Try to move up; apply only if ball stays inside window
        new_y = self.y - self.step
        if new_y - self.radius >= 0:
            self.y = new_y

    def move_down(self):
        # Try to move down; apply only if ball stays inside window
        new_y = self.y + self.step
        if new_y + self.radius <= self.screen_height:
            self.y = new_y

    def draw(self, screen):
        # Draw red ball at current (x, y)
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius)
