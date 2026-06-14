# src/view/tela_jogo_corrigida.py
import sys
import os
import io
import pygame
from sys import exit

ROOT_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")
)
sys.path.insert(0, ROOT_DIR)

from src.core.game import Monopoly
from src.core.propriedade import TipoCasa

# ---------------------------------------------------------------------------
# CONSTANTES
# ---------------------------------------------------------------------------
GAME_WIDTH  = 1920
GAME_HEIGHT = 1040
PLAYER_WIDTH  = 65
PLAYER_HEIGHT = 75

ANIM_FPS = 8

# Cores
DOURADO      = (255, 215, 0)
DOURADO_ESC  = (180, 140, 0)
FUNDO_ESCURO = (20, 15, 5)
BRANCO       = (255, 255, 255)
PRETO        = (0, 0, 0)

# Caminho dos assets unificado
SPRITES_BASE = os.path.join(ROOT_DIR, "assets", "images", "sprites", "peoes")

# Janela global de renderização
window = pygame.display.set_mode((GAME_WIDTH, GAME_HEIGHT))
pygame.display.set_caption("Technopoly")

# Instanciação tardia do game engine dentro de executar_jogo()
game = None
anims = []
n_jogadores_ativos = 4

# ---------------------------------------------------------------------------
# UTILS E FALLBACK DE SPRITES (ESTREITAMENTE PNG)
# ---------------------------------------------------------------------------
def _superficie_fallback(cor: tuple, w: int, h: int, label: str = "") -> pygame.Surface:
    """Gera um bloco visual caso o arquivo PNG falte no disco."""
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(surf, cor, (0, 0, w, h), border_radius=8)
    if label:
        fonte = pygame.font.SysFont("Arial", 20, bold=True)
        txt = fonte.render(label, True, BRANCO)
        surf.blit(txt, (w // 2 - txt.get_width() // 2, h // 2 - txt.get_height() // 2))
    return surf

DIRECOES       = ["R", "L", "T", "B"]
N_FRAMES       = 6
CORES_FALLBACK = [(220, 50, 50), (50, 100, 220), (50, 180, 50), (220, 180, 50), (180, 50, 180), (50, 180, 180), (200, 120, 50)]

def _carregar_sprites(personagem_id: int) -> dict:
    """Carrega as animações de caminhada e frame estático em PNG."""
    pasta = os.path.join(SPRITES_BASE, f"PERSONAGEM{personagem_id}")
    cor   = CORES_FALLBACK[(personagem_id - 1) % len(CORES_FALLBACK)]

    def fallback():
        return _superficie_fallback(cor, PLAYER_WIDTH, PLAYER_HEIGHT, f"P{personagem_id}")

    sprites = {}

    # Carrega frames de movimento
    for direcao in DIRECOES:
        frames = []
        for i in range(1, N_FRAMES + 1):
            caminho = os.path.join(pasta, f"RUN-{i}-{direcao}.png")
            if os.path.isfile(caminho):
                img = pygame.image.load(caminho).convert_alpha()
                img = pygame.transform.scale(img, (PLAYER_WIDTH, PLAYER_HEIGHT))
                frames.append(img)
            else:
                frames.append(fallback())
        sprites[direcao] = frames

    # CORREÇÃO CRÍTICA DO BUG DA TUPLA: Carrega o frame parado estritamente como Surface
    caminho_stop = os.path.join(pasta, "STOP.png")
    if os.path.isfile(caminho_stop):
        try:
            surf = pygame.image.load(caminho_stop).convert_alpha()
            surf = pygame.transform.scale(surf, (PLAYER_WIDTH, PLAYER_HEIGHT))
        except Exception:
            surf = fallback()
    else:
        surf = fallback()
        
    sprites["STOP"] = [surf]
    return sprites

# Dicionário global de Sprites mapeando os IDs de 1 a 7
#SPRITES = {i: _carregar_sprites(i) for i in range(1, 8)}
SPRITES = {}

# Mapeamento de Casas do Tabuleiro
CASAS = [
    (1680, 130), (1635, 180), (1635, 240), (1635, 310), (1635, 410), (1635, 500), (1635, 590), (1635, 670), (1635, 780),
    (1750, 885), (1550, 800), (1430, 800), (1300, 800), (1150, 800), (1040, 800), (900,  800), (740,  800), (600,  800),
    (440,  800), (310,  800), (160,  885), (230,  795), (230,  705), (230,  615), (230,  525), (230,  435), (230,  345),
    (230,  255), (230,  165), (230,  130), (300,  130), (420,  130), (580,  130), (700,  130), (910,  130), (1050, 130),
    (1190, 130), (1330, 130), (1450, 130), (1580, 130)
]

# Recursos de Imagem estáticos
tabuleiro_img = pygame.image.load(os.path.join("images", "tabuleiro.png"))
tabuleiro_img = pygame.transform.scale(tabuleiro_img, (GAME_WIDTH, GAME_HEIGHT))

dados_imagens = {}
for i in range(1, 7):
    img = pygame.image.load(os.path.join("images", f"dado{i}.png")).convert_alpha()
    dados_imagens[i] = pygame.transform.scale(img, (80, 80))

clock = pygame.time.Clock()

pygame.init()
pygame.font.init()

# Fontes
fonte_titulo  = pygame.font.SysFont("Arial", 36, bold=True)
fonte_normal  = pygame.font.SysFont("Arial", 24)
fonte_pequena = pygame.font.SysFont("Arial", 18)
fonte_card    = pygame.font.SysFont("Arial", 20, bold=True)
fonte_card_sm = pygame.font.SysFont("Arial", 16)

# ---------------------------------------------------------------------------
# GERENCIAMENTO DE ANIMAÇÕES
# ---------------------------------------------------------------------------
class EstadoAnim:
    def __init__(self):
        self.frame_idx = 0.0
        self.direcao   = "STOP"
        self.movendo   = False

    def atualizar(self, dt_ms: int, char_id: int):
        if self.movendo and self.direcao != "STOP":
            self.frame_idx += (ANIM_FPS * dt_ms) / 1000.0
            total = len(SPRITES[char_id][self.direcao])
            if self.frame_idx >= total:
                self.frame_idx = 0.0

    def get_frame(self, char_id: int) -> pygame.Surface:
        direcao = self.direcao if self.movendo else "STOP"
        frames  = SPRITES[char_id].get(direcao, SPRITES[char_id]["STOP"])
        idx     = int(self.frame_idx) % len(frames)
        return frames[idx]

    def iniciar_movimento(self, direcao: str):
        self.direcao   = direcao
        self.movendo   = True
        self.frame_idx = 0.0

    def parar(self):
        self.movendo   = False
        self.direcao   = "STOP"
        self.frame_idx = 0.0

def _calcular_direcao(pos_atual: int, proxima: int) -> str:
    if pos_atual >= len(CASAS) or proxima >= len(CASAS):
        return "R"
    ax, ay = CASAS[pos_atual]
    bx, by = CASAS[proxima]
    dx, dy = bx - ax, by - ay
    if abs(dx) >= abs(dy):
        return "R" if dx >= 0 else "L"
    else:
        return "B" if dy >= 0 else "T"

# ---------------------------------------------------------------------------
# ESTADOS DE CONTROLE
# ---------------------------------------------------------------------------
passos_restantes     = 0
tempo_movimento      = 0
jogador_atual_idx    = 0
ultimo_dado_1        = 1
ultimo_dado_2        = 1
aguardando_popup     = False
popup_ativo          = False
popup_titulo         = ""
popup_texto          = ""
popup_eh_propriedade = False

TIPOS_COMPRAVEIS = {TipoCasa.PROPRIEDADE}
OFFSETS          = [(0, 0), (18, 0), (0, 18), (18, 18)]

def get_pos_jogador(idx: int) -> tuple[int, int]:
    pos = game.jogadores[idx].posicao % len(CASAS)
    x, y = CASAS[pos]
    ox, oy = OFFSETS[idx % 4]
    return x + ox, y + oy

# ---------------------------------------------------------------------------
# CARD DO JOGADOR AJUSTADO (MAIS PARA BAIXO)
# ---------------------------------------------------------------------------
CARD_X   = 330
CARD_Y   = 230  # Mudado de 170 para 230 para ficar mais baixo na zona interna
CARD_W   = 310
LINHA_H  = 22
PADDING  = 14

CARD_SPRITE_W = 80
CARD_SPRITE_H = 92

def _get_stop_sprite(personagem_num: int) -> pygame.Surface:
    frame = SPRITES[personagem_num]["STOP"][0]
    return pygame.transform.smoothscale(frame, (CARD_SPRITE_W, CARD_SPRITE_H))

def desenhar_card_jogador():
    if not game: return
    j = game.jogadores[jogador_atual_idx]
    
    # Busca qual o ID real do herói escolhido na seleção de personagens
    # Se o engine monopoly não salvar o ID escolhido, usaremos o ID do loop como fallback seguro
    personagem_num = getattr(j, 'personagem_id', jogador_atual_idx + 1)

    n_props = len(j.propriedades)
    CARD_H = max(CARD_SPRITE_H + PADDING * 2 + 90, 180 + max(0, n_props - 1) * LINHA_H)

    fundo = pygame.Surface((CARD_W, CARD_H), pygame.SRCALPHA)
    fundo.fill((20, 15, 5, 215))
    window.blit(fundo, (CARD_X, CARD_Y))

    pygame.draw.rect(window, DOURADO, (CARD_X, CARD_Y, CARD_W, CARD_H), width=3, border_radius=18)

    sprite_surf = _get_stop_sprite(personagem_num)
    window.blit(sprite_surf, (CARD_X + PADDING, CARD_Y + PADDING))

    sep_x = CARD_X + PADDING + CARD_SPRITE_W + 10
    pygame.draw.line(window, DOURADO_ESC, (sep_x, CARD_Y + PADDING), (sep_x, CARD_Y + CARD_SPRITE_H + PADDING), 1)

    texto_x = sep_x + 10
    y = CARD_Y + PADDING

    surf = fonte_card.render(f"✦ {j.nome}", True, DOURADO)
    window.blit(surf, (texto_x, y))
    y += 26

    surf = fonte_card_sm.render(f"Herói P{personagem_num}", True, (180, 180, 180))
    window.blit(surf, (texto_x, y))
    y += 22

    surf = fonte_card.render(f"$ {j.saldo:,}", True, BRANCO)
    window.blit(surf, (texto_x, y))

    sep_y = CARD_Y + CARD_SPRITE_H + PADDING + 8
    pygame.draw.line(window, DOURADO_ESC, (CARD_X + PADDING, sep_y), (CARD_X + CARD_W - PADDING, sep_y), 1)
    y = sep_y + 8

    surf = fonte_card_sm.render("Propriedades:", True, DOURADO)
    window.blit(surf, (CARD_X + PADDING, y))
    y += LINHA_H + 2

    if not j.propriedades:
        surf = fonte_card_sm.render("  Nenhuma ainda", True, (140, 140, 140))
        window.blit(surf, (CARD_X + PADDING, y))
    else:
        for pid in j.propriedades:
            prop = game.tabuleiro.get_casa(pid)
            andares_str = f" [{prop.andares}🏠]" if prop.andares > 0 else ""
            hip_str     = " (Hip.)" if prop.hipotecada else ""
            texto_prop  = f"  • {prop.nome}{andares_str}{hip_str}"

            while fonte_card_sm.size(texto_prop)[0] > CARD_W - PADDING * 2 and len(texto_prop) > 5:
                texto_prop = texto_prop[:-2] + "…"

            surf = fonte_card_sm.render(texto_prop, True, BRANCO)
            window.blit(surf, (CARD_X + PADDING, y))
            y += LINHA_H

def desenhar_popup():
    if not popup_ativo: return
    PX, PY, PW, PH = 560, 230, 800, 420
    pygame.draw.rect(window, FUNDO_ESCURO, (PX, PY, PW, PH), border_radius=25)
    pygame.draw.rect(window, DOURADO, (PX, PY, PW, PH), width=4, border_radius=25)

    surf_titulo = fonte_titulo.render(popup_titulo, True, DOURADO)
    window.blit(surf_titulo, (PX + 40, PY + 30))

    pygame.draw.line(window, DOURADO_ESC, (PX + 40, PY + 80), (PX + PW - 40, PY + 80), 1)

    y_texto = PY + 100
    for linha in popup_texto.split("\n"):
        surf = fonte_normal.render(linha, True, BRANCO)
        window.blit(surf, (PX + 40, y_texto))
        y_texto += 34

    opcoes = "[C] Comprar     [P] Passar" if popup_eh_propriedade else "[P] Continuar"
    surf_op = fonte_normal.render(opcoes, True, DOURADO)
    window.blit(surf_op, (PX + 140, PY + PH - 55))

def draw():
    window.blit(tabuleiro_img, (0, 0))

    # Renderiza os peões na quantidade exata de jogadores configurados
    for idx in range(n_jogadores_ativos):
        j = game.jogadores[idx]
        personagem_num = getattr(j, 'personagem_id', idx + 1)
        frame = anims[idx].get_frame(personagem_num)
        x, y  = get_pos_jogador(idx)
        window.blit(frame, (x, y))

    # Painel de dados
    painel_x, painel_y = 760, 650
    pygame.draw.rect(window, FUNDO_ESCURO, (painel_x, painel_y, 400, 140), border_radius=20)
    pygame.draw.rect(window, DOURADO, (painel_x, painel_y, 400, 140), width=4, border_radius=20)

    window.blit(dados_imagens[ultimo_dado_1], (painel_x + 70,  painel_y + 30))
    window.blit(dados_imagens[ultimo_dado_2], (painel_x + 230, painel_y + 30))

    soma_surf = fonte_titulo.render(f"= {ultimo_dado_1 + ultimo_dado_2}", True, DOURADO)
    window.blit(soma_surf, (painel_x + 160, painel_y + 95))

    desenhar_card_jogador()
    desenhar_popup()

# ---------------------------------------------------------------------------
# LOOP PRINCIPAL DO CORE DO JOGO (DINÂMICO)
# ---------------------------------------------------------------------------
def executar_jogo(lista_jogadores_config=None):
    global popup_ativo, popup_titulo, popup_texto, popup_eh_propriedade
    global ultimo_dado_1, ultimo_dado_2, passos_restantes, tempo_movimento
    global jogador_atual_idx, aguardando_popup, game, anims, n_jogadores_ativos, SPRITES

    # 1. Se o dicionário de sprites estiver vazio, carrega (Correção do bug anterior)
    if not SPRITES:
        SPRITES.update({i: _carregar_sprites(i) for i in range(1, 8)})
        
    # 2. DEFESA CONTRA NONE (CORREÇÃO ATUAL): Mover o fallback para ANTES do len()
    if lista_jogadores_config is None:
        lista_jogadores_config = [
            {"nome": "Jogador 1", "personagem": 1},
            {"nome": "Jogador 2", "personagem": 2}
        ]

    # 3. Agora sim podemos ler o tamanho e mapear com total segurança!
    n_jogadores_ativos = len(lista_jogadores_config)
    nomes_pure = [item["nome"] for item in lista_jogadores_config]
    
    # Inicializa o motor central de simulação Monopoly com os nomes corretos
    game = Monopoly(nomes_pure)
    
    # Aloca e vincula o ID do Personagem dentro de cada objeto Jogador do motor
    for i, cfg in enumerate(lista_jogadores_config):
        game.jogadores[i].personagem_id = cfg["personagem"]

    anims = [EstadoAnim() for _ in range(n_jogadores_ativos)]
    pos_antes_mover = [j.posicao for j in game.jogadores]
    while True:
        dt = clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if event.type == pygame.KEYDOWN:
                if aguardando_popup:
                    casa_atual = game.tabuleiro.get_casa(game.jogadores[jogador_atual_idx].posicao)
                    if event.key == pygame.K_c and popup_eh_propriedade:
                        from src.core import transacoes
                        transacoes.comprar_propriedade(game.jogadores[jogador_atual_idx], casa_atual)
                        popup_ativo      = False
                        aguardando_popup = False
                        anims[jogador_atual_idx].parar()
                        jogador_atual_idx = (jogador_atual_idx + 1) % n_jogadores_ativos

                    elif event.key == pygame.K_p:
                        popup_ativo      = False
                        aguardando_popup = False
                        anims[jogador_atual_idx].parar()
                        jogador_atual_idx = (jogador_atual_idx + 1) % n_jogadores_ativos

                
                elif event.key == pygame.K_SPACE:
                    if passos_restantes == 0 and not aguardando_popup:
                        resultado        = game.dados.rolar()
                        ultimo_dado_1    = resultado.dado1
                        ultimo_dado_2    = resultado.dado2
                        passos_restantes = resultado.total
                        pos_antes_mover[jogador_atual_idx] = game.jogadores[jogador_atual_idx].posicao

        # Lógica de atualização de posições passo a passo
        tempo_movimento += 1
        if tempo_movimento > 4 and passos_restantes > 0:
            tempo_movimento = 0
            j = game.jogadores[jogador_atual_idx]
            pos_old = j.posicao
            j.posicao = (j.posicao + 1) % len(CASAS)
            passos_restantes -= 1

            direcao = _calcular_direcao(pos_old, j.posicao)
            anims[jogador_atual_idx].iniciar_movimento(direcao)

            if passos_restantes == 0:
                anims[jogador_atual_idx].parar()
                casa = game.tabuleiro.get_casa(j.posicao)

                popup_eh_propriedade = (casa.tipo in TIPOS_COMPRAVEIS and casa.esta_disponivel())
                popup_ativo      = True
                popup_titulo     = casa.nome
                aguardando_popup = True

                if casa.tipo == TipoCasa.PROPRIEDADE:
                    dono = game.jogadores[casa.dono_id].nome if casa.dono_id is not None else "Disponível"
                    popup_texto = (
                        f"Preço:        ${casa.preco}\n"
                        f"Aluguel base: ${casa.aluguel_base}\n"
                        f"Hipoteca:     ${casa.valor_hipoteca}\n"
                        f"Custo andar:  ${casa.preco_andar}\n"
                        f"Dono: {dono}"
                    )
                elif casa.tipo == TipoCasa.SORTE:
                    popup_texto = "Você caiu em Sorte!\nSaque uma carta."
                elif casa.tipo == TipoCasa.AZAR:
                    popup_texto = "Você caiu em Azar!\nSaque uma carta."
                elif casa.tipo == TipoCasa.FERIAS:
                    popup_texto = "Hora de descansar!\nVocê está de férias."
                elif casa.tipo == TipoCasa.PRISAO:
                    popup_texto = "Apenas visitando a prisão.\nNada acontece."
                elif casa.tipo == TipoCasa.IR_PARA_PRISAO:
                    popup_texto = "Vá direto para a prisão!\nNão passe pelo Início."
                elif casa.tipo == TipoCasa.IMPOSTO:
                    popup_texto = "Imposto de Renda!\nPague $200 ao banco."
                elif casa.tipo == TipoCasa.INICIO:
                    popup_texto = "Você passou pelo Início!\nReceba $200."
                else:
                    popup_texto = "Casa sem efeito especial."

        for idx, anim in enumerate(anims):
            p_id = getattr(game.jogadores[idx], 'personagem_id', idx + 1)
            anim.atualizar(dt, p_id)

        draw()
        pygame.display.update()

if __name__ == "__main__":
    # Garante que o jogo comece pelo Menu Principal, desencadeando as telas certas!
    menu = TelaMenu()
    print("🖥️ Inicializando a janela gráfica do Pygame...")
    resultado = menu.rodar_menu()
    
    if resultado == "INICIAR":
        print("👥 Abrindo a seleção de personagens...")
        tela_selecao = TelaSelecao(menu.tela)
        lista_jogadores = tela_selecao.rodar()
        
        if lista_jogadores:
            print("🎲 Iniciando o Tabuleiro com os jogadores configurados!")
            executar_jogo(lista_jogadores)