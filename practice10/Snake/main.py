import pygame  # game library for window, drawing, events, timing
import sys  # used for clean program exit
from snake import Food, Snake  # import our custom game objects

def show_score(score):
    # Create text surface that shows current score and level
    score_surf = font.render(f"Score: {score} Level: {level}",False,(255,255,255))
    # Place text near top-center of the screen
    score_rect = score_surf.get_rect(center = (360,50))
    # Draw the text on the game screen
    screen.blit(score_surf,score_rect)

pygame.init()  # initialize pygame modules before using them

font = pygame.font.Font(None,40)  # default font, size 40

cell_size = 30  # pixel size of one grid cell
number_of_cells = 25  # grid is 25x25 cells

Screen_w = cell_size * number_of_cells  # total screen width
Screen_h = cell_size * number_of_cells  # total screen height

screen = pygame.display.set_mode((Screen_w, Screen_h))  # create game window
clock = pygame.time.Clock()  # controls FPS (frame rate)

f = Food(5,6)  # create food object (x,y args are ignored in current class)
s = Snake(12,12)  # create snake at center-ish position

score = 0  # points collected
level = 1  # game speed level

SNAKE_UPDATE = pygame.USEREVENT  # custom event id for snake movement tick
pygame.time.set_timer(SNAKE_UPDATE, 200 * level)  # movement every 200 ms at level 1

while True:  # main game loop runs forever until quit
    for i in pygame.event.get():
        if i.type == pygame.QUIT:
            pygame.quit()  # close pygame
            sys.exit()  # stop Python program

        if i.type == SNAKE_UPDATE:
            s.update()  # move snake one step on each timer tick

        if i.type == pygame.KEYDOWN:
            # WASD controls; forbid instant 180-degree turns
            if i.key == pygame.K_w and s.direction != [0,1]:
                s.direction = [0,-1]
            if i.key == pygame.K_s and s.direction != [0,-1]:
                s.direction = [0,1]
            if i.key == pygame.K_a and s.direction != [1,0]:
                s.direction = [-1,0]
            if i.key == pygame.K_d and s.direction != [-1,0]:
                s.direction = [1,0]

    
    # Check if snake head touched food
    if s.body[0] == [f.pos_x,f.pos_y]:
        score +=1  # increase score
        print(score)  # print score in terminal (debug/info)
        f.new_food()  # move food to random new position
        # Grow snake by duplicating its current last segment
        s.body.append([s.body[len(s.body) - 1][0] , s.body[len(s.body) - 1][1]])
        # Level up every 3 points
        if score >= 3 and score % 3 == 0:
            level += 1
            # Increase speed by reducing timer interval
            pygame.time.set_timer(SNAKE_UPDATE, 200 // level)
    
    # Game over if snake hits itself or leaves map bounds
    if s.body[0] in s.body[1:] or (s.body[0][0] > 24 or s.body[0][0] < 0) or (s.body[0][1] > 24 or s.body[0][1] < 0):
        pygame.quit()
        sys.exit()
        

    
    screen.fill("Black")  # clear old frame with black background

    
    f.draw()  # draw food
    s.draw()  # draw snake

    show_score(score)  # draw score/level text

    pygame.display.update()  # show everything drawn this frame
    clock.tick(60)  # limit loop to 60 FPS
