import pygame
import random

cell_size = 30
screen = pygame.display.set_mode((750,750))

class Food:
    def __init__(self,x,y):
        self.pos_x, self.pos_y = self.random_pos()

    def draw(self):
        food_rect = pygame.Rect(self.pos_x * cell_size, self.pos_y * cell_size, cell_size, cell_size)
        pygame.draw.rect(screen,("Red"),food_rect)

    def random_pos(self):
        self.pos_x = random.randint(0,24)
        self.pos_y = random.randint(0,24)

        return self.pos_x,self.pos_y
    
    def new_food(self):
        self.random_pos()

class Snake:
    def __init__(self,x,y):
        self.body = [[x,y],[x-1,y],[x-2,y]] #starting snake 
        self.direction = [1,0]
        

    def draw(self):
        for i in self.body:
            i_rect = (i[0] * cell_size, i[1] * cell_size, cell_size , cell_size)
            pygame.draw.rect(screen, (255,255,255),i_rect)

    def update(self):
        self.body = self.body[:-1] #delete last segment 

        new_x = self.body[0][0] + self.direction[0]       
        new_y = self.body[0][1] + self.direction[1]

        self.body.insert(0, [new_x, new_y]) #new segment