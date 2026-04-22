import pygame
import sys

pygame.init()

Screen_w = 900
Screen_h = 900

active_size = 0
active_color = (255,255,255)
active_shape = "circle"   
painting = []
screen = pygame.display.set_mode((Screen_w,Screen_h))

clock = pygame.time.Clock()


def draw_menu():
    pygame.draw.rect(screen, 'grey', [0, 0, Screen_w, 70])
    pygame.draw.line(screen,"black", (0,70), (Screen_w,70), 3)
    Super_large_brush = pygame.draw.rect(screen, 'black', [10,10,50,50])               #menu and brush bottons
    pygame.draw.circle(screen, 'white', (35,35),20)
    Large_brush = pygame.draw.rect(screen, 'black', [70,10,50,50])
    pygame.draw.circle(screen, 'white', (95,35),15)
    Medium_brush = pygame.draw.rect(screen, 'black', [130,10,50,50])
    pygame.draw.circle(screen, 'white', (155,35),10)
    Small_brush = pygame.draw.rect(screen, 'black', [190,10,50,50])
    pygame.draw.circle(screen, 'white', (215,35),5)

    Rectangle_brush = pygame.draw.rect(screen, 'black', [250,10,50,50])
    pygame.draw.rect(screen, 'white', [262,22,25,25])


    red = pygame.draw.rect(screen, (255,0,0),[Screen_w - 35, 10,25,25])
    blue = pygame.draw.rect(screen, (0,0,255),[Screen_w - 35, 35,25,25])
    green = pygame.draw.rect(screen, (0,255,0),[Screen_w - 60, 10 ,25,25])
    yellow = pygame.draw.rect(screen, (255,255,0),[Screen_w - 60, 35,25,25])
    teal = pygame.draw.rect(screen, (0,255,255),[Screen_w - 85, 10,25,25])                      #color bottons
    purple = pygame.draw.rect(screen, (255,0,255),[Screen_w - 85, 35,25,25])
    black = pygame.draw.rect(screen, (0,0,0),[Screen_w - 110, 10,25,25])
    white = pygame.draw.rect(screen, (255,255,255),[Screen_w - 110, 35,25,25])

    eraser = pygame.draw.rect(screen, 'black', [310,10,50,50])
    pygame.draw.rect(screen, 'grey', [320,20,30,30])

    brush_list = [Super_large_brush,Large_brush,Medium_brush,Small_brush,Rectangle_brush,eraser]
    color_list = [red,blue,green,yellow,teal,purple,black,white]
    rgb_list = [(255,0,0), (0,0,255), (0,255,0), (255,255,0), (0,255,255), (255,0,255), (0,0,0), (255,255,255)]

    return brush_list,color_list,rgb_list

def draw_painting(paints):
    for paint in paints:
        color, pos, size, shape = paint
        
        if shape == "circle":
            pygame.draw.circle(screen, color, pos, size)
        elif shape == "rect":
            pygame.draw.rect(screen, color, (pos[0], pos[1], size*2, size*2))

while True:
    screen.fill((255,255,255))
    brushes, colors, rgbs = draw_menu()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.MOUSEBUTTONDOWN:
            for i in range(len(brushes)):
                if brushes[i].collidepoint(event.pos):
                    if i == 4:      # Rectangle
                        active_shape = "rect"
                    elif i == 5:        # Eraser
                        active_shape = "circle"
                        active_color = (255,255,255)
                    else:
                        active_shape = "circle"
                        active_size = 20 - (i * 5)
        if event.type == pygame.MOUSEBUTTONDOWN:
            for i in range(len(colors)):
                if colors[i].collidepoint(event.pos):
                    active_color = rgbs[i]

        


        
            
    

    mouse = pygame.mouse.get_pos()
    left_click = pygame.mouse.get_pressed()[0] 
    
    
    if left_click and mouse[1] > 70:
        painting.append((active_color, mouse, active_size, active_shape))

    draw_painting(painting)
    
    if mouse[1] > 70:         #checks if mouse not on the menu
        if active_shape == "circle":
            pygame.draw.circle(screen, active_color, mouse, active_size)
        else:
            pygame.draw.rect(screen, active_color, (mouse[0], mouse[1], active_size*2, active_size*2))

   


    


    
    pygame.display.update()
    clock.tick(500)             #smoother lines with higher fps