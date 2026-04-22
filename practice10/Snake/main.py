import pygame
import sys
from snake import Food, Snake

def show_score(score):
    score_surf = font.render(f"Score: {score} Level: {level}",False,(255,255,255))
    score_rect = score_surf.get_rect(center = (360,50))
    screen.blit(score_surf,score_rect)

pygame.init()

font = pygame.font.Font(None,40)

cell_size = 30 
number_of_cells = 25        

Screen_w = cell_size * number_of_cells        #use grid system
Screen_h = cell_size * number_of_cells

screen = pygame.display.set_mode((Screen_w, Screen_h))
clock = pygame.time.Clock()

f = Food(5,6)
s = Snake(12,12)

score = 0
level = 1

SNAKE_UPDATE = pygame.USEREVENT
pygame.time.set_timer(SNAKE_UPDATE, 200 * level) #speed of snake

while True:
    for i in pygame.event.get():
        if i.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if i.type == SNAKE_UPDATE:
            s.update()

        if i.type == pygame.KEYDOWN:
            if i.key == pygame.K_w and s.direction != [0,1]: #change direction and forbide 180 turn
                s.direction = [0,-1]
            if i.key == pygame.K_s and s.direction != [0,-1]:
                s.direction = [0,1]
            if i.key == pygame.K_a and s.direction != [1,0]:
                s.direction = [-1,0]
            if i.key == pygame.K_d and s.direction != [-1,0]:
                s.direction = [1,0]

    
    if s.body[0] == [f.pos_x,f.pos_y]: #collision things with food   and  level increase
        score +=1
        print(score)
        f.new_food()
        s.body.append([s.body[len(s.body) - 1][0] , s.body[len(s.body) - 1][1]]) #adds new segment at the coordinates of last segment that alrady moved
        if score >= 3 and score % 3 == 0:
            level += 1
            pygame.time.set_timer(SNAKE_UPDATE, 200 // level)
           # itself without head                  x coordinate                            y coordinate
    
    if s.body[0] in s.body[1:] or (s.body[0][0] > 24 or s.body[0][0] < 0) or (s.body[0][1] > 24 or s.body[0][1] < 0): #collision things with itself and walls
        pygame.quit()
        sys.exit()
        

    
    screen.fill("Black")

    
    f.draw()
    s.draw()

    show_score(score)

   


    

    pygame.display.update()
    clock.tick(60)