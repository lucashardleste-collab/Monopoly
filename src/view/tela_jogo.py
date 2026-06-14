import sys
import os

ROOT_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")
)

sys.path.insert(0, ROOT_DIR)

import pygame
from sys import exit

from src.core.game import Monopoly

passos_restantes = 0
tempo_movimento = 0
jogador_atual = 0

# Game Variables
GAME_WIDTH = 1920
GAME_HEIGHT = 1040

PLAYER_WIDTH = 65
PLAYER_HEIGHT = 75

current_frame = 0
animation_speed = 0.01

pygame.init()

game = Monopoly([
    "Capivara",
    "Urso",
    "Cristo",
    "Guaxinim"
])

print("Total de casas:", game.tabuleiro.total)

# Images
frames = [
    pygame.image.load(os.path.join("images", "tabuleiro.png")),
]

CASAS = [

    # 0 = PARTIDA (canto superior direito)
    (1680, 130),

    # DESCENDO PELA DIREITA
    (1635, 180),  # 1
    (1635, 240),  # 2
    (1635, 310),  # 3
    (1635, 410),  # 4
    (1635, 500),  # 5
    (1635, 590),  # 6
    (1635, 670),  # 7
    (1635, 780),  # 8

    # VÁ PARA PRISÃO
    (1750, 885),  # 9

    # INDO PARA ESQUERDA (parte de baixo)
    (1550, 800),  # 10
    (1430, 800),  # 11
    (1300, 800),  # 12
    (1150, 800),  # 13
    (1040, 800),   # 14
    (900, 800),   # 15
    (740, 800),   # 16
    (600, 800),   # 17
    (440, 800),   # 18
    (310, 800),   # 19

    # FÉRIAS
    (160, 885),   # 20

    # SUBINDO PELA ESQUERDA
    (230, 795),   # 21
    (230, 705),   # 22
    (230, 615),   # 23
    (230, 525),   # 24
    (230, 435),   # 25
    (230, 345),   # 26
    (230, 255),   # 27

    # PRISÃO
    (230, 165),   # 28

    # INDO PARA DIREITA (parte de cima)
    (230, 130),   # 29
    (300, 130),   # 30
    (420, 130),   # 31
    (580, 130),   # 32
    (700, 130),   # 33
    (910, 130),  # 34
    (1050, 130),  # 35
    (1190, 130),  # 36
    (1330, 130),  # 37

    # FECHAMENTO
    (1450, 130),  # 38
    (1580, 130),  # 39
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

    # evita sobreposição
    player2.x += 15

    player3.y += 15

    player4.x += 15
    player4.y += 15

def draw():

    window.blit(
        frames[int(current_frame)],
        (0, 0)
    )

    # marcadores coloridos
    pygame.draw.circle(
        window,
        (255, 0, 0),
        (player1.centerx, player1.centery),
        12
    )

    pygame.draw.circle(
        window,
        (0, 0, 255),
        (player2.centerx, player2.centery),
        12
    )

    pygame.draw.circle(
        window,
        (0, 255, 0),
        (player3.centerx, player3.centery),
        12
    )

    pygame.draw.circle(
        window,
        (255, 255, 0),
        (player4.centerx, player4.centery),
        12
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

                if passos_restantes == 0:

                    resultado = game.dados.rolar()

                    try:
                        passos_restantes = resultado.total
                    except:
                        passos_restantes = resultado

                    print(
                        f"Turno: {game.jogadores[jogador_atual].nome}"
                    )

                    print(
                        f"Andará {passos_restantes} casas"
                    )

        tempo_movimento += 1

        if tempo_movimento > 1:

            tempo_movimento = 0

            if passos_restantes > 0:

                game.jogadores[jogador_atual].mover(
                 1,
                 len(CASAS)
                )
                passos_restantes -= 1

                if passos_restantes == 0:

                    print(f"Fim do turno de {game.jogadores[jogador_atual].nome}"
                    )

                    jogador_atual += 1

                    if jogador_atual >= len(game.jogadores):
                        jogador_atual = 0

                    print(
                        f"Próximo jogador: {game.jogadores[jogador_atual].nome}"
                    )

                    print(
                        f"Posição: {game.jogadores[0].posicao}"
                    )

        current_frame += animation_speed

        if current_frame >= len(frames):
                       current_frame = 0

        atualizar_posicoes()

        draw()

        pygame.display.update()
        clock.tick(60)