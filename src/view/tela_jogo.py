import sys
import os

ROOT_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")
)

sys.path.insert(0, ROOT_DIR)

import pygame
from sys import exit

from src.core.game import Monopoly
from src.core.propriedade import TipoCasa

aguardando_popup = False

passos_restantes = 0
tempo_movimento = 0
jogador_atual = 0
ultimo_dado_1 = 1
ultimo_dado_2 = 1

popup_ativo = False
popup_titulo = ""
popup_texto = ""

# Game Variables
GAME_WIDTH = 1920
GAME_HEIGHT = 1040

PLAYER_WIDTH = 65
PLAYER_HEIGHT = 75

current_frame = 0
animation_speed = 0.01

pygame.init()

game = Monopoly([
    "Guaxinim",
    "Capivara",
    "Cristo",
    "Urso"
])

print("Total de casas:", game.tabuleiro.total)

# Images
frames = [
    pygame.image.load(os.path.join("images", "tabuleiro.png")),
]

def desenhar_popup():

    if not popup_ativo:
        return

    pygame.draw.rect(
        window,
        (20, 20, 20),
        (560, 250, 800, 400),
        border_radius=25
    )

    pygame.draw.rect(
        window,
        (255, 215, 0),
        (560, 250, 800, 400),
        width=4,
        border_radius=25
    )

    fonte_titulo = pygame.font.SysFont(
        "Arial",
        40,
        bold=True
    )

    fonte_texto = pygame.font.SysFont(
        "Arial",
        28
    )

    titulo = fonte_titulo.render(
        popup_titulo,
        True,
        (255, 215, 0)
    )

    texto = fonte_texto.render(
        popup_texto,
        True,
        (255,255,255)
    )

    fonte_opcao = pygame.font.SysFont(
    "Arial",
    24,
    bold=True
    )

    opcao = fonte_opcao.render(
        "[C] Comprar   [P] Passar",
        True,
        (255,255,255)
    )

    window.blit(opcao, (700, 520))

    window.blit(titulo, (650, 300))
    window.blit(texto, (650, 380))


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

dados_imagens = {}

for i in range(1, 7):
    img = pygame.image.load(
        os.path.join("images", f"dado{i}.png")
    ).convert_alpha()

    img = pygame.transform.scale(
        img,
        (80, 80)
    )

    dados_imagens[i] = img

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
    # Painel dourado
    painel_x = 760
    painel_y = 650
    painel_largura = 400
    painel_altura = 140

    pygame.draw.rect(
        window,
        (30, 20, 5),  # fundo escuro
        (painel_x, painel_y, painel_largura, painel_altura),
        border_radius=20
    )

    pygame.draw.rect(
        window,
        (255, 215, 0),  # borda dourada
        (painel_x, painel_y, painel_largura, painel_altura),
        width=4,
        border_radius=20
    )

    fonte = pygame.font.SysFont("Arial", 30, bold=True)
    texto = fonte.render(
        f"= {ultimo_dado_1 + ultimo_dado_2}",
        True,
        (255, 215, 0)
    )

    window.blit(
        texto,
        (painel_x + 165, painel_y + 90)
    )

    window.blit(
    dados_imagens[ultimo_dado_1],
    (painel_x + 70, painel_y + 30)
    )

    window.blit(
        dados_imagens[ultimo_dado_2],
        (painel_x + 230, painel_y + 30)
    )

    desenhar_popup()
# Game Loop
def executar_jogo():
    global popup_ativo
    global popup_titulo
    global popup_texto
    global ultimo_dado_1
    global ultimo_dado_2
    global passos_restantes
    global tempo_movimento
    global jogador_atual
    global current_frame
    global aguardando_popup

    while True:

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if event.type == pygame.KEYDOWN:

                if aguardando_popup:

                    if event.key == pygame.K_c:

                        print("COMPROU")

                        popup_ativo = False
                        aguardando_popup = False

                        jogador_atual += 1

                        if jogador_atual >= len(game.jogadores):
                            jogador_atual = 0

                    elif event.key == pygame.K_p:

                        print("PASSOU")

                        popup_ativo = False
                        aguardando_popup = False

                        jogador_atual += 1

                        if jogador_atual >= len(game.jogadores):
                            jogador_atual = 0


                if event.key == pygame.K_SPACE:

                    if passos_restantes == 0 and not aguardando_popup:

                        resultado = game.dados.rolar()
                        ultimo_dado_1 = resultado.dado1
                        ultimo_dado_2 = resultado.dado2
                        print(ultimo_dado_1)
                        print(ultimo_dado_2)

                        try:
                            passos_restantes = resultado.total
                        except:
                            passos_restantes = resultado

                        print(
                            f"Turno: {game.jogadores[jogador_atual].nome}"
                        )

        tempo_movimento += 1

        if tempo_movimento > 4:

            tempo_movimento = 0

            if passos_restantes > 0:

                game.jogadores[jogador_atual].mover(
                    1,
                    len(CASAS)
                )

                passos_restantes -= 1

                if passos_restantes == 0:

                    casa = game.tabuleiro.get_casa(
                    game.jogadores[jogador_atual].posicao
                    )

                    print(
                        "POS:",
                        game.jogadores[jogador_atual].posicao
                    )

                    print(
                        "CASA:",
                        game.tabuleiro.get_casa(
                            game.jogadores[jogador_atual].posicao
                        ).nome
                    )

                    popup_ativo = True
                    popup_titulo = casa.nome
                    aguardando_popup = True

                    if casa.tipo == TipoCasa.PROPRIEDADE:

                        popup_texto = (
                            f"Preço: ${casa.preco}\n"
                            f"Aluguel: ${casa.aluguel_base}\n"
                            f"Hipoteca: ${casa.valor_hipoteca}\n"
                            f"Custo Andar: ${casa.preco_andar}"
                        )

                    elif casa.tipo == TipoCasa.SORTE:

                        popup_texto = "Você caiu em Sorte!"

                    elif casa.tipo == TipoCasa.NADA:

                        popup_texto = "Zona Neutra"

                    elif casa.tipo == TipoCasa.FERIAS:

                        popup_texto = "Hora de descansar!"

                    elif casa.tipo == TipoCasa.PRISAO:

                        popup_texto = "Visitando a prisão"

                    print("CAIU EM:", casa.nome)

            
        current_frame += animation_speed

        if current_frame >= len(frames):
            current_frame = 0

        atualizar_posicoes()

        draw()

        pygame.display.update()

        clock.tick(60)

if __name__ == "__main__":
    executar_jogo()