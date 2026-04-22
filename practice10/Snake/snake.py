import pygame  # drawing and rectangle utilities
import random  # random food position generation

cell_size = 30  # same grid cell size as in main.py
screen = pygame.display.set_mode((750,750))  # surface where snake/food is drawn

class Food:
    def __init__(self,x,y):
        # Store first random position for food
        self.pos_x, self.pos_y = self.random_pos()

    def draw(self):
        # Convert grid coords to pixel rectangle and draw red food block
        food_rect = pygame.Rect(self.pos_x * cell_size, self.pos_y * cell_size, cell_size, cell_size)
        pygame.draw.rect(screen,("Red"),food_rect)

    def random_pos(self):
        # Pick random x/y inside 25x25 grid (0..24)
        self.pos_x = random.randint(0,24)
        self.pos_y = random.randint(0,24)

        # Return generated coordinates as tuple
        return self.pos_x,self.pos_y
    
    def new_food(self):
        # Public method to move food to a new random position
        self.random_pos()

class Snake:
    def __init__(self,x,y):
        self.body = [[x,y],[x-1,y],[x-2,y]]  # starting snake body (head first)
        self.direction = [1,0]  # starting move direction: to the right
        

    def draw(self):
        # Draw each segment of snake body as white block
        for i in self.body:
            i_rect = (i[0] * cell_size, i[1] * cell_size, cell_size , cell_size)
            pygame.draw.rect(screen, (255,255,255),i_rect)

    def update(self):
        # Remove tail so length stays same during normal movement
        self.body = self.body[:-1]

        # Compute new head position using current direction
        new_x = self.body[0][0] + self.direction[0]       
        new_y = self.body[0][1] + self.direction[1]

        # Insert new head at beginning of body list
        self.body.insert(0, [new_x, new_y])
