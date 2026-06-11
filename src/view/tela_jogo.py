import pygame
from sys import exit #to terminate the program
import os


#dfdsfdsfdsf

#game variables
GAME_WIDTH= 1920
GAME_HEIGHT= 1040
PLayer_Y = GAME_HEIGHT/2
PLayer_X = GAME_WIDTH/2
PLayer_WIDTH = 49
PLayer_HEIGHT = 60
PLayer_SPEED = 8

current_frame = 0
animation_speed = 0.01


#images
frames = [
    pygame.image.load(os.path.join("images", "tabuleiro.png")),
    
]

frames = [
    pygame.transform.scale(frame, (1920, 1040))
    for frame in frames
]

player_image_right = pygame.image.load(os.path.join("images", "golem.png"))
player_image_right = pygame.transform.scale(player_image_right, (PLayer_WIDTH, PLayer_HEIGHT))

pygame.init() #always needed to initalize pygame
window = pygame.display.set_mode((GAME_WIDTH, GAME_HEIGHT))
pygame.display.set_caption("Banco de TI")  #title of the window
pygame.display.set_icon(player_image_right)  
clock = pygame.time.Clock() #used for the frame rate

class Player(pygame.Rect):
    def __init__(self):
        pygame.Rect.__init__(self, PLayer_X, PLayer_Y, PLayer_WIDTH, PLayer_HEIGHT)
        self.image = player_image_right

#left (x), top (y), width, height

player = Player()


def draw():
    window.blit(
        frames[int(current_frame)],
        (0,0)
    )
    window.blit(player.image, player)


# game loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: #users closes by pressing the X button
            pygame.quit()
            exit()
        '''
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP or event.key == pygame.K_w:
                player.y -= 5
            if event.key == pygame.K_DOWN or event.key == pygame.K_s:
                player.y += 5
            if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                player.x += 5
            if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                player.x -= 5
        '''
    keys = pygame.key.get_pressed()

    if keys[pygame.K_UP] or keys[pygame.K_w]:
        player.y -= PLayer_SPEED
    if keys[pygame.K_DOWN] or keys[pygame.K_s]:
        player.y += PLayer_SPEED
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        player.x += PLayer_SPEED;
    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
        player.x -= PLayer_SPEED;
    
    if(player.x < 0):
        player.x = 0
    if(player.x > GAME_WIDTH - PLayer_WIDTH):
        player.x = GAME_WIDTH - PLayer_WIDTH
    if(player.y < 0):
        player.y = 0
    if(player.y > GAME_HEIGHT - PLayer_HEIGHT):
        player.y = GAME_HEIGHT - PLayer_HEIGHT

    current_frame += animation_speed

    if current_frame >= len(frames):
        current_frame = 0

    draw()
    pygame.display.update()
    clock.tick(120) #Frames per second