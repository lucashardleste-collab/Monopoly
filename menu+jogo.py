import pygame
from sys import exit  # to terminate the program
import os

# --- VARIÁVEIS DE CONFIGURAÇÃO DO JOGO ---
GAME_WIDTH = 1300
GAME_HEIGHT = 660

PLayer_Y = GAME_HEIGHT / 2
PLayer_X = GAME_WIDTH / 2
PLayer_WIDTH = 49
PLayer_HEIGHT = 60
PLayer_SPEED = 8

current_frame = 0.0
animation_speed = 0.1

# --- INICIALIZAÇÃO DO PYGAME ---
pygame.init()
window = pygame.display.set_mode((GAME_WIDTH, GAME_HEIGHT))
pygame.display.set_caption("Banco de TI - Monopoly Empire")
clock = pygame.time.Clock()

# ─── ESTADO DO FLUXO DE TELAS ───
# O jogo começa na tela de "MENU". Quando clicar em Iniciar, muda para "JOGO"
estado_tela = "MENU"

# --- RECURSOS DO MENU (AVANÇADO) ---
caminho_menu = os.path.join("images", "Menu_imagem.png")
try:
    imagem_menu = pygame.image.load(caminho_menu)
    imagem_menu = pygame.transform.scale(imagem_menu, (GAME_WIDTH, GAME_HEIGHT))
except pygame.error:
    print(f"⚠️ Imagem do menu não encontrada em: {caminho_menu}")
    print("Usando um fundo preto alternativo para o menu temporariamente.")
    imagem_menu = None

# Retângulos de colisão recalculados para caber na resolução de 1300x660
# Se os botões ficarem desalinhados, altere o segundo número (Y) dessas duas linhas:
retangulo_iniciar = pygame.Rect(440, 340, 420, 90)
retangulo_sair = pygame.Rect(440, 430, 420, 90)

# --- RECURSOS DO JOGO (TEUS FRAMES E JOGADOR) ---
frames = [
    pygame.image.load(os.path.join("images", "tabuleiro.png")),
]
frames = [
    pygame.transform.scale(frame, (GAME_WIDTH, GAME_HEIGHT))
    for frame in frames
]

player_image_right = pygame.image.load(os.path.join("images", "P1.png"))
player_image_right = pygame.transform.scale(player_image_right, (PLayer_WIDTH, PLayer_HEIGHT))
player_image_left = pygame.transform.flip(player_image_right, True, False)

pygame.display.set_icon(player_image_right)


class Player(pygame.Rect):
    def __init__(self):
        pygame.Rect.__init__(self, PLayer_X, PLayer_Y, PLayer_WIDTH, PLayer_HEIGHT)
        self.image = player_image_right


player = Player()


def draw_game():
    """Desenha os elementos da partida ativa."""
    window.blit(frames[int(current_frame)], (0, 0))
    window.blit(player.image, player)


def draw_menu():
    """Desenha os elementos do menu principal."""
    if imagem_menu:
        window.blit(imagem_menu, (0, 0))
    else:
        window.fill((15, 15, 30))  # Azul escuro se a imagem faltar

    # Captura posição do mouse para efeito visual de hover (borda de luz)
    posicao_rato = pygame.mouse.get_pos()

    if retangulo_iniciar.collidepoint(posicao_rato):
        pygame.draw.rect(window, (214, 160, 0), retangulo_iniciar, 3, border_radius=15)
    if retangulo_sair.collidepoint(posicao_rato):
        pygame.draw.rect(window, (214, 160, 0), retangulo_sair, 3, border_radius=15)


# ─── LOOP PRINCIPAL UNIFICADO ───
while True:

    # 1. PROCESSAMENTO DE EVENTOS GLOBAL
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

        # Cliques do mouse específicos quando o Menu está aberto
        if estado_tela == "MENU" and event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Clique esquerdo
                if retangulo_iniciar.collidepoint(event.pos):
                    estado_tela = "JOGO"  # Troca o estado, iniciando a partida!
                elif retangulo_sair.collidepoint(event.pos):
                    pygame.quit()
                    exit()

    # 2. MAQUINA DE FLUXO (O que processar baseado no estado_tela)
    if estado_tela == "MENU":
        # Renderiza o menu
        draw_menu()

    elif estado_tela == "JOGO":
        # Processa a movimentação do teu jogo original
        keys = pygame.key.get_pressed()

        if keys[pygame.K_UP] or keys[pygame.K_w]:
            player.y -= PLayer_SPEED
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            player.y += PLayer_SPEED
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            player.x += PLayer_SPEED
            player.image = player_image_right
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            player.x -= PLayer_SPEED
            player.image = player_image_left

        # Restrições de tela (Bordas)
        if player.x < 0:
            player.x = 0
        if player.x > GAME_WIDTH - PLayer_WIDTH:
            player.x = GAME_WIDTH - PLayer_WIDTH
        if player.y < 0:
            player.y = 0
        if player.y > GAME_HEIGHT - PLayer_HEIGHT:
            player.y = GAME_HEIGHT - PLayer_HEIGHT

        # Lógica de animação do cenário
        current_frame += animation_speed
        if current_frame >= len(frames):
            current_frame = 0

        # Renderiza a partida
        draw_game()

    # 3. ATUALIZAÇÃO DA TELA
    pygame.display.update()
    clock.tick(120)