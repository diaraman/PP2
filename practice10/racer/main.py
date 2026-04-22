import sys
import pygame
import random
from race import Player
from race import Enemy
from race import Coin

def show_score(score):
    score_surf = font.render(f"Score: {score}",False,(255,255,255))
    score_rect = score_surf.get_rect(center = (360,50))
    screen.blit(score_surf,score_rect)

pygame.init()

Screen_W = 500
Screen_H = 900

screen = pygame.display.set_mode((Screen_W,Screen_H))

road_surf = pygame.image.load('racer/img/road.webp').convert_alpha()
clock = pygame.time.Clock()

objects = pygame.sprite.Group()               #create sprite groups for each object
player_group = pygame.sprite.Group()
coin_group = pygame.sprite.Group()


player = Player(250,850)
e = Enemy()
coin = Coin()


objects.add(e)
player_group.add(player)
coin_group.add(coin)                            #add them in groups


score = 0
font = pygame.font.Font(None,40)



SPAWN_ENEMY = pygame.USEREVENT + 1
pygame.time.set_timer(SPAWN_ENEMY, 2000)               #timer fot enemy

SPAWN_COIN = pygame.USEREVENT + 2
pygame.time.set_timer(SPAWN_COIN, 3600)               #timer for coin

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            player.move(event)

        if event.type == SPAWN_ENEMY:
            e = Enemy()
            objects.add(e)

        if event.type == SPAWN_COIN:
            c = Coin()
            coin_group.add(c)

    rand = random.randint(100,400)

    screen.fill((0,130,0))
    screen.blit(road_surf,(75,0))


    objects.update()
    objects.draw(screen)
    player_group.draw(screen)
    coin_group.update()
    coin_group.draw(screen)

    show_score(score)

    if player.check_collisions(objects):                 #what happens when collide with enemy
        pygame.quit()
        sys.exit()

    if player.check_collisions_coin(coin_group):                 #what happens when collide with coin
        score += 1

    
    


    pygame.display.update()
    clock.tick(60)