import pygame  # import pygame library
import random  # import random module

# Create sprite classes

class Player(pygame.sprite.Sprite):  # define Player class inheriting from Sprite
    def __init__(self, x_pos, y_pos):  # initialize Player with position
        pygame.sprite.Sprite.__init__(self)  # call parent init
        self.image = pygame.image.load('racer/img/player_car.png')  # load player car image
        self.image = pygame.transform.scale(self.image, (100, 100))  # scale image to 100x100
        self.rect = self.image.get_rect()  # get rect from image
        self.rect.center = (x_pos, y_pos)  # set center to given position

    def move(self, event):  # move method for player
        if event.key == pygame.K_d:  # if D key pressed
            self.rect.x += 25  # move right
        elif event.key == pygame.K_a:  # if A key pressed
            self.rect.x -= 25  # move left

    def check_collisions(self, objects):  # check collision with objects
        return pygame.sprite.spritecollide(self, objects, False)  # return collision result

    def check_collisions_coin(self, coin_group):  # check collision with coins
        return pygame.sprite.spritecollide(self, coin_group, True)  # return and remove coin

class Enemy(pygame.sprite.Sprite):  # define Enemy class
    def __init__(self):  # initialize Enemy
        pygame.sprite.Sprite.__init__(self)  # call parent init
        self.image = pygame.image.load("racer/img/enemy_car.png")  # load enemy car image
        self.image = pygame.transform.scale(self.image, (100, 100))  # scale image
        self.rect = self.image.get_rect()  # get rect
        self.rect.center = (random.randint(100, 400), 0)  # set random x, y=0

    def update(self):  # update method
        self.rect.y += 6  # move down

class Coin(pygame.sprite.Sprite):  # define Coin class
    def __init__(self):  # initialize Coin
        pygame.sprite.Sprite.__init__(self)  # call parent init
        self.image = pygame.image.load('racer/img/coin.png')  # load coin image
        self.image = pygame.transform.scale(self.image, (40, 40))  # scale image
        self.rect = self.image.get_rect()  # get rect
        self.rect.center = (random.randint(100, 400), 0)  # set random x, y=0

    def update(self):  # update method
        self.rect.y += 5  # move down