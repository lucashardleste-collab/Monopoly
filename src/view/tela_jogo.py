import sys
import os

ROOT_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")
)

sys.path.insert(0, ROOT_DIR)

import pygame
from sys import exit

from src.core.game import Monopoly


# Game Variables
GAME_WIDTH = 1920
GAME_HEIGHT = 1040

PLAYER_WIDTH = 69
PLAYER_HEIGHT = 80

current_frame = 0
animation_speed = 0.01

pygame.init()

game = Monopoly([
    "Capivara",
    "Urso",
    "Cristo",
    "Guaxinim"
])
# Images
frames = [
    pygame.image.load(os.path.join("images", "tabuleiro.png")),
]

CASAS = [

    # TOPO
    (1580, 70),   # 0
    (1450, 70),   # 1
    (1320, 70),   # 2
    (1190, 70),   # 3
    (1060, 70),   # 4
    (930, 70),    # 5
    (800, 70),    # 6
    (670, 70),    # 7
    (540, 70),    # 8
    (410, 70),    # 9

    # PRISÃO
    (220, 70),    # 10

    # ESQUERDA
    (220, 180),   # 11
    (220, 280),   # 12
    (220, 380),   # 13
    (220, 480),   # 14
    (220, 580),   # 15
    (220, 680),   # 16
    (220, 780),   # 17
    (220, 880),   # 18

    # FÉRIAS
    (220, 950),   # 19

    # BAIXO
    (380, 950),   # 20
    (510, 950),   # 21
    (640, 950),   # 22
    (770, 950),   # 23
    (900, 950),   # 24
    (1030, 950),  # 25
    (1160, 950),  # 26
    (1290, 950),  # 27
    (1420, 950),  # 28
    (1550, 950),  # 29

    # VÁ PARA PRISÃO
    (1700, 950),  # 30

    # DIREITA
    (1700, 850),  # 31
    (1700, 750),  # 32
    (1700, 650),  # 33
    (1700, 550),  # 34
    (1700, 450),  # 35
    (1700, 350),  # 36
    (1700, 250),  # 37
    (1700, 150),  # 38

    (1700, 70),   # 39
]

frames = [
    pygame.transform.scale(frame, (GAME_WIDTH, GAME_HEIGHT))
    for frame in frames
]
window = pygame.display.set_mode((GAME_WIDTH, GAME_HEIGHT))
# Jogadores
player1_image = pygame.image.load(os.path.join("images", "P1.png")).convert_alpha()
player1_image = pygame.transform.scale(player1_image, (PLAYER_WIDTH, PLAYER_HEIGHT))

player2_image = pygame.image.load(os.path.join("images", "P2.png")).convert_alpha()
player2_image = pygame.transform.scale(player2_image, (PLAYER_WIDTH, PLAYER_HEIGHT))

player3_image = pygame.image.load(os.path.join("images", "P3.png")).convert_alpha()
player3_image = pygame.transform.scale(player3_image, (PLAYER_WIDTH, PLAYER_HEIGHT))

player4_image = pygame.image.load(os.path.join("images", "P4.png")).convert_alpha()
player4_image = pygame.transform.scale(player4_image, (PLAYER_WIDTH, PLAYER_HEIGHT))

# Window
pygame.display.set_caption("Technopoly")

# Ícone da janela
pygame.display.set_icon(player1_image)

clock = pygame.time.Clock()


class Player(pygame.Rect):
    def __init__(self, x, y, image):
        super().__init__(x, y, PLAYER_WIDTH, PLAYER_HEIGHT)
        self.image = image


# 4 jogadores no canto superior direito
player1 = Player(0, 0, player1_image)
player2 = Player(0, 0, player2_image)
player3 = Player(0, 0, player3_image)
player4 = Player(0, 0, player4_image)

def atualizar_posicoes():

    j1 = game.jogadores[0]
    j2 = game.jogadores[1]
    j3 = game.jogadores[2]
    j4 = game.jogadores[3]

    player1.x, player1.y = CASAS[j1.posicao]
    player2.x, player2.y = CASAS[j2.posicao]
    player3.x, player3.y = CASAS[j3.posicao]
    player4.x, player4.y = CASAS[j4.posicao]

    # deslocamento para não sobrepor
    player2.x += 20
    player3.y += 20

    player4.x += 20
    player4.y += 20

def draw():
    window.blit(
        frames[int(current_frame)],
        (0, 0)
    )

    window.blit(player1.image, player1)
    window.blit(player2.image, player2)
    window.blit(player3.image, player3)
    window.blit(player4.image, player4)


# Game Loop
while True:

   for event in pygame.event.get():

    if event.type == pygame.QUIT:
        pygame.quit()
        exit()

    if event.type == pygame.KEYDOWN:

        if event.key == pygame.K_SPACE:

            print("ESPACO APERTADO")

            resultado = game.dados.rolar()

            game.jogadores[0].mover(
                resultado.total,
                len(CASAS)
            )

            print(
                f"Posicao: {game.jogadores[0].posicao}"
            )

    atualizar_posicoes()
    draw()

    pygame.display.update()
    clock.tick(120)