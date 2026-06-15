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

# --- IMPORTS DOS TEUS MÓDULOS DE LÓGICA (CORE) ---
from src.core import cartas
# Se precisares de tipos específicos do enum de cartas:
from src.core.cartas import TipoEfeito
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
    
    # Define a cor da borda de forma inteligente com base no tipo de evento
    if popup_eh_carta:
        if "SORTE" in popup_titulo:
            cor_borda_dinamica = (50, 220, 100)  # Verde Neon para Sorte
        else:
            cor_borda_dinamica = (220, 50, 50)   # Vermelho Alerta para Azar
    else:
        cor_borda_dinamica = DOURADO              # Dourado Clássico para propriedades e bancos

    # Desenha o fundo e a borda customizada
    pygame.draw.rect(window, FUNDO_ESCURO, (PX, PY, PW, PH), border_radius=25)
    pygame.draw.rect(window, cor_borda_dinamica, (PX, PY, PW, PH), width=4, border_radius=25)

    # Título do Popup
    surf_titulo = fonte_titulo.render(popup_titulo, True, cor_borda_dinamica)
    window.blit(surf_titulo, (PX + 40, PY + 30))

    pygame.draw.line(window, DOURADO_ESC, (PX + 40, PY + 80), (PX + PW - 40, PY + 80), 1)

    # Renderização do texto em linhas
    y_texto = PY + 110
    for linha in popup_texto.split("\n"):
        surf = fonte_normal.render(linha, True, BRANCO)
        window.blit(surf, (PX + 40, y_texto))
        y_texto += 34

    # Instrução de botões na parte de baixo
    if popup_eh_propriedade:
        opcoes = "[C] Comprar       [P] Passar Vez"
    else:
        opcoes = "[P] Fechar e Continuar"
        
    surf_op = fonte_normal.render(opcoes, True, cor_borda_dinamica)
    window.blit(surf_op, (PX + 40, PY + PH - 55))

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
popup_eh_carta = False  # Nova flag para sabermos se o popup atual é uma carta sacada
carta_atual_objeto = None

def executar_jogo(lista_jogadores_config=None):
    global popup_ativo, popup_titulo, popup_texto, popup_eh_propriedade, popup_eh_carta, carta_atual_objeto
    global ultimo_dado_1, ultimo_dado_2, passos_restantes, tempo_movimento
    global jogador_atual_idx, aguardando_popup, game, anims, n_jogadores_ativos, SPRITES

    if not SPRITES:
        print("📦 Carregando sprites de peões...")
        SPRITES.update({i: _carregar_sprites(i) for i in range(1, 8)})
        
    if lista_jogadores_config is None:
        lista_jogadores_config = [
            {"nome": "Jogador 1", "personagem": 1},
            {"nome": "Jogador 2", "personagem": 2}
        ]

    n_jogadores_ativos = len(lista_jogadores_config)
    nomes_pure = [item["nome"] for item in lista_jogadores_config]
    
    game = Monopoly(nomes_pure)
    
    for i, cfg in enumerate(lista_jogadores_config):
        game.jogadores[i].personagem_id = cfg["personagem"]

    anims = [EstadoAnim() for _ in range(n_jogadores_ativos)]
    
    # IMPORTANTE: Criamos os baralhos de Sorte e Azar usando a lógica do seu cartas.py
    baralho_sorte = cartas.criar_deck_sorte()
    baralho_azar  = cartas.criar_deck_azar()

    print(f"🎮 Jogo Iniciado! Vez de: {game.jogadores[jogador_atual_idx].nome}.")

    while True:
        dt = clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if event.type == pygame.KEYDOWN:
                if aguardando_popup:
                    casa_atual = game.tabuleiro.get_casa(game.jogadores[jogador_atual_idx].posicao)
                    
                    # Caso 1: Fechamento de Popups de Ação comuns ou de Cartas
                    if event.key == pygame.K_p:
                        print(f"↩️ {game.jogadores[jogador_atual_idx].nome} fechou o evento/passou a vez.")
                        
                        # Se a carta que ele acabou de ler mandou ele se mover (ex: Vá para o Início ou Vá para a Prisão),
                        # a posição dele já mudou na lógica, então atualizamos os passos para o peão andar na tela.
                        if popup_eh_carta and carta_atual_objeto:
                            # Se a carta alterou a posição mas não deu passos de animação, podemos forçar o peão a ir
                            pass
                        
                        popup_ativo      = False
                        aguardando_popup = False
                        popup_eh_carta   = False
                        carta_atual_objeto = None
                        anims[jogador_atual_idx].parar()
                        
                        # Passa o turno para o próximo player
                        jogador_atual_idx = (jogador_atual_idx + 1) % n_jogadores_ativos
                        print(f"🎲 Vez de: {game.jogadores[jogador_atual_idx].nome}. Pressione ESPAÇO.")

                    # Caso 2: Compra de Propriedade
                    elif event.key == pygame.K_c and popup_eh_propriedade:
                        print(f"💰 {game.jogadores[jogador_atual_idx].nome} comprou {casa_atual.nome}.")
                        from src.core import transacoes
                        transacoes.comprar_propriedade(game.jogadores[jogador_atual_idx], casa_atual)
                        
                        popup_ativo      = False
                        aguardando_popup = False
                        anims[jogador_atual_idx].parar()
                        jogador_atual_idx = (jogador_atual_idx + 1) % n_jogadores_ativos
                        print(f"🎲 Vez de: {game.jogadores[jogador_atual_idx].nome}. Pressione ESPAÇO.")

                # Se não tem popup ativo, aceita rolar o dado
                elif event.key == pygame.K_SPACE:
                    if passos_restantes == 0 and not aguardando_popup:
                        resultado = game.dados.rolar()
                        ultimo_dado_1 = resultado.dado1
                        ultimo_dado_2 = resultado.dado2
                        passos_restantes = resultado.total
                        
                        j = game.jogadores[jogador_atual_idx]
                        pos_antiga = j.posicao
                        
                        # LOG VISUAL DO BÔNUS DE INÍCIO:
                        # Usando a lógica do seu motor, se ao somar os passos ele ultrapassar a casa 40, ganha o bônus
                        if pos_antiga + passos_restantes >= 40:
                            print(f"🏪 {j.nome} vai passar pelo INÍCIO nesta jogada e receberá +$200!")

        # Lógica de movimentação frame por frame do peão
        if passos_restantes > 0 and not aguardando_popup:
            tempo_movimento += 1
            if tempo_movimento > 6:
                tempo_movimento = 0
                j = game.jogadores[jogador_atual_idx]
                pos_old = j.posicao
                
                # Avança 1 casa por vez para fazer a animação andar bonita
                j.posicao = (j.posicao + 1) % 40
                passos_restantes -= 1

                # INTERCEPTAÇÃO DO BÔNUS DE INÍCIO: Se pisou exatamente na casa 0 (Início)
                if j.posicao == 0:
                    # Aplica a regra de negócio do seu transacoes.py ou adiciona direto no saldo
                    j.saldo += 200
                    print(f"💰 BÔNUS ATIVADO: {j.nome} cruzou o ponto de partida. +$200 adicionados ao saldo! Saldo atual: ${j.saldo}")

                direcao = _calcular_direcao(pos_old, j.posicao)
                anims[jogador_atual_idx].iniciar_movimento(direcao)

                # Quando o peão termina de andar todos os passos rolandos no dado
                if passos_restantes == 0:
                    anims[jogador_atual_idx].parar()
                    casa = game.tabuleiro.get_casa(j.posicao)
                    print(f"📍 {j.nome} parou na casa: {casa.nome} ({casa.tipo})")

                    popup_eh_propriedade = (casa.tipo in TIPOS_COMPRAVEIS and casa.esta_disponivel())
                    popup_eh_carta = False
                    popup_ativo = True
                    popup_titulo = casa.nome
                    aguardando_popup = True

# ─── LOGICA INTEGRADA PARA CASAS DE SORTE ───
                    if casa.tipo == TipoCasa.SORTE:
                        popup_eh_carta = True
                        
                        # Usa a função .sacar() do seu objeto Deck
                        carta = baralho_sorte.sacar() 
                        carta_atual_objeto = carta
                        
                        # Importamos o módulo de transações exigido pelo aplicador
                        from src.core import transacoes 
                        
                        # Executa o processador oficial do seu cartas.py
                        resultado_carta = cartas.aplicar_carta(
                            carta=carta,
                            jogador_atual=j,
                            todos_jogadores=game.jogadores,
                            tabuleiro=game.tabuleiro,
                            transacoes_mod=transacoes
                        )
                        
                        popup_titulo = "🍀 CARTA DE SORTE"
                        popup_texto = f"Mensagem:\n{carta.descricao}"
                        
                        # SE A CARTA MANDOU O PEÃO SE MOVER (Ex: Avance até o Início / Avv. São João)
                        if resultado_carta["moveu"] and resultado_carta["nova_posicao"] is not None:
                            # Sincroniza a posição gráfica para o peão ser teleportado/movido na tela
                            # Se a carta mandou ir para a prisão (casa 10), o resultado já cuida disso
                            pass
                            
                        print(f"🃏 {j.nome} aplicou Sorte: {carta.descricao}")

                    # ─── LOGICA INTEGRADA PARA CASAS DE AZAR ───
                    elif casa.tipo == TipoCasa.AZAR:
                        popup_eh_carta = True
                        
                        # Usa a função .sacar() do seu objeto Deck
                        carta = baralho_azar.sacar()
                        carta_atual_objeto = carta
                        
                        from src.core import transacoes
                        
                        # Executa o processador oficial do seu cartas.py
                        resultado_carta = cartas.aplicar_carta(
                            carta=carta,
                            jogador_atual=j,
                            todos_jogadores=game.jogadores,
                            tabuleiro=game.tabuleiro,
                            transacoes_mod=transacoes
                        )
                        
                        popup_titulo = "💥 CARTA DE AZAR"
                        popup_texto = f"Mensagem:\n{carta.descricao}"
                        
                        print(f"🃏 {j.nome} aplicou Azar: {carta.descricao}")

                    # ─── OUTRAS CASAS DO TABULEIRO ───
                    elif casa.tipo == TipoCasa.PROPRIEDADE:
                        dono = game.jogadores[casa.dono_id].nome if casa.dono_id is not None else "Disponível"
                        popup_texto = (
                            f"Preço:        ${casa.preco}\n"
                            f"Aluguel base: ${casa.aluguel_base}\n"
                            f"Hipoteca:     ${casa.valor_hipoteca}\n"
                            f"Custo andar:  ${casa.preco_andar}\n"
                            f"Dono: {dono}"
                        )
                    elif casa.tipo == TipoCasa.INICIO:
                        popup_texto = "Ponto de Partida Technopoly!\nVocê coletou os benefícios de passagem."
                    elif casa.tipo == TipoCasa.PRISAO:
                        popup_texto = "Visita simples à Prisão.\nVocê está apenas observando os detentos."
                    elif casa.tipo == TipoCasa.IR_PARA_PRISAO:
                        popup_texto = "Infração detectada!\nSeu peão foi enviado direto para a delegacia."
                        # Aplica a lógica de prisão do seu jogador.py
                        j.entrar_na_prisao()
                    elif casa.tipo == TipoCasa.IMPOSTO:
                        j.saldo -= 200
                        popup_texto = "Imposto sobre Grandes Fortunas de Software!\nVocê pagou $200 ao banco."
                    else:
                        popup_texto = "Área Neutra.\nNenhum evento financeiro nesta casa."
                    
                    print(f"📢 Popup Ativo: {popup_titulo}. Aguardando confirmação...")

        # Atualização das animações
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