# src/view/tela_selecao_corrigida.py
import pygame
import os
import sys

# ---------------------------------------------------------------------------
# CONSTANTES
# ---------------------------------------------------------------------------
LARGURA  = 1920
ALTURA   = 1040
DOURADO     = (255, 215, 0)
DOURADO_ESC = (180, 140, 0)
FUNDO       = (10, 8, 5)
BRANCO      = (255, 255, 255)
CINZA       = (160, 160, 160)
CINZA_ESC   = (60, 60, 60)
VERDE       = (50, 200, 100)
VERMELHO    = (200, 60, 60)

N_PERSONAGENS = 7     # PERSONAGEM1 … PERSONAGEM7
MAX_JOGADORES = 4
MIN_JOGADORES = 2

# Tamanho do preview do sprite na tela de seleção
SPRITE_W = 120
SPRITE_H = 140

ROOT_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")
)

# Caminho unificado idêntico ao do main.py
SPRITES_BASE = os.path.join(ROOT_DIR, "assets", "images", "sprites", "peoes")


# ---------------------------------------------------------------------------
# GERENCIAMENTO DE ASSETS (APENAS PNG)
# ---------------------------------------------------------------------------
def _superficie_fallback(idx: int, w: int, h: int) -> pygame.Surface:
    """Gera um retângulo colorido caso o PNG não exista em disco."""
    CORES = [
        (220, 60, 60), (60, 100, 220), (60, 180, 60),
        (220, 180, 50), (180, 60, 220), (60, 200, 200), (220, 120, 60),
    ]
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    cor  = CORES[idx % len(CORES)]
    pygame.draw.rect(surf, cor, (0, 0, w, h), border_radius=14)
    pygame.draw.rect(surf, DOURADO, (0, 0, w, h), width=2, border_radius=14)
    fonte = pygame.font.SysFont("Arial", 28, bold=True)
    label = fonte.render(f"P{idx + 1}", True, BRANCO)
    surf.blit(label, (w // 2 - label.get_width() // 2, h // 2 - label.get_height() // 2))
    return surf


def _carregar_sprites_selecao() -> list[pygame.Surface]:
    """Carrega estritamente o STOP.png de cada uma das 7 pastas."""
    sprites = []
    for i in range(1, N_PERSONAGENS + 1):
        pasta = os.path.join(SPRITES_BASE, f"PERSONAGEM{i}")
        caminho_png = os.path.join(pasta, "STOP.png")
        
        if os.path.isfile(caminho_png):
            try:
                surf = pygame.image.load(caminho_png).convert_alpha()
                surf = pygame.transform.smoothscale(surf, (SPRITE_W, SPRITE_H))
            except Exception as e:
                print(f"[ERRO] Falha ao carregar {caminho_png}: {e}")
                surf = _superficie_fallback(i - 1, SPRITE_W, SPRITE_H)
        else:
            print(f"[AVISO] Arquivo ausente, usando fallback para: {caminho_png}")
            surf = _superficie_fallback(i - 1, SPRITE_W, SPRITE_H)
            
        sprites.append(surf)
    return sprites


# ---------------------------------------------------------------------------
# COMPONENTES UI
# ---------------------------------------------------------------------------
class InputTexto:
    def __init__(self, x, y, w, h, placeholder=""):
        self.rect        = pygame.Rect(x, y, w, h)
        self.texto       = ""
        self.ativo       = False
        self.placeholder = placeholder
        self.fonte       = pygame.font.SysFont("Arial", 26)
        self.cursor_vis  = True
        self.cursor_timer = 0

    def evento(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.ativo = self.rect.collidepoint(event.pos)
        if event.type == pygame.KEYDOWN and self.ativo:
            if event.key == pygame.K_BACKSPACE:
                self.texto = self.texto[:-1]
            elif event.key not in (pygame.K_RETURN, pygame.K_TAB):
                if len(self.texto) < 16:
                    self.texto += event.unicode

    def atualizar(self, dt):
        self.cursor_timer += dt
        if self.cursor_timer > 500:
            self.cursor_vis   = not self.cursor_vis
            self.cursor_timer = 0

    def desenhar(self, surf):
        cor_borda = DOURADO if self.ativo else CINZA_ESC
        pygame.draw.rect(surf, (25, 20, 10), self.rect, border_radius=10)
        pygame.draw.rect(surf, cor_borda, self.rect, width=2, border_radius=10)

        if self.texto:
            label = self.fonte.render(self.texto, True, BRANCO)
        else:
            label = self.fonte.render(self.placeholder, True, (80, 80, 80))
        surf.blit(label, (self.rect.x + 12, self.rect.y + 8))

        if self.ativo and self.cursor_vis:
            cx = self.rect.x + 12 + self.fonte.size(self.texto)[0] + 2
            cy = self.rect.y + 8
            pygame.draw.line(surf, DOURADO, (cx, cy), (cx, cy + 28), 2)


class BotaoPersonagem:
    def __init__(self, x, y, sprite: pygame.Surface, idx: int):
        self.rect        = pygame.Rect(x, y, SPRITE_W + 20, SPRITE_H + 50)
        self.sprite      = sprite
        self.idx         = idx      
        self.hover       = False
        self.fonte       = pygame.font.SysFont("Arial", 18, bold=True)

    def atualizar(self, pos_mouse):
        self.hover = self.rect.collidepoint(pos_mouse)

    def clicado(self, pos) -> bool:
        return self.rect.collidepoint(pos)

    def desenhar(self, surf, usado_por: str | None, selecionado_por_mim: bool):
        alfa = 220 if (selecionado_por_mim or self.hover) else 140
        fundo = pygame.Surface(self.rect.size, pygame.SRCALPHA)
        pygame.draw.rect(fundo, (40, 30, 5, alfa), (0, 0, *self.rect.size), border_radius=14)
        surf.blit(fundo, self.rect.topleft)

        if selecionado_por_mim:
            cor_borda, espessura = DOURADO, 3
        elif usado_por:
            cor_borda, espessura = VERMELHO, 2
        elif self.hover:
            cor_borda, espessura = DOURADO_ESC, 2
        else:
            cor_borda, espessura = (70, 60, 30), 1

        pygame.draw.rect(surf, cor_borda, self.rect, width=espessura, border_radius=14)

        if usado_por and not selecionado_por_mim:
            escuro = self.sprite.copy()
            escuro.fill((40, 40, 40, 250), special_flags=pygame.BLEND_RGBA_MULT)
            surf.blit(escuro, (self.rect.x + 10, self.rect.y + 8))
        else:
            surf.blit(self.sprite, (self.rect.x + 10, self.rect.y + 8))

        if usado_por:
            label = self.fonte.render(usado_por[:10], True, BRANCO if selecionado_por_mim else CINZA)
        else:
            label = self.fonte.render(f"P{self.idx + 1}", True, DOURADO if self.hover else CINZA)
            
        surf.blit(label, (self.rect.x + self.rect.w // 2 - label.get_width() // 2, self.rect.y + self.rect.h - 26))


class Botao:
    def __init__(self, x, y, w, h, texto, cor_borda=None):
        self.rect      = pygame.Rect(x, y, w, h)
        self.texto     = texto
        self.cor_borda = cor_borda or DOURADO
        self.hover     = False
        self.fonte     = pygame.font.SysFont("Arial", 26, bold=True)

    def atualizar(self, pos):
        self.hover = self.rect.collidepoint(pos)

    def clicado(self, pos) -> bool:
        return self.rect.collidepoint(pos)

    def desenhar(self, surf):
        cor_fundo = (50, 38, 5) if self.hover else (25, 18, 3)
        pygame.draw.rect(surf, cor_fundo, self.rect, border_radius=14)
        pygame.draw.rect(surf, self.cor_borda, self.rect, width=3, border_radius=14)
        label = self.fonte.render(self.texto, True, self.cor_borda)
        surf.blit(label, (self.rect.centerx - label.get_width() // 2, self.rect.centery - label.get_height() // 2))


# ---------------------------------------------------------------------------
# TELA DE SELEÇÃO
# ---------------------------------------------------------------------------
class TelaSelecao:
    def __init__(self, tela: pygame.Surface):
        self.tela    = tela
        self.clock   = pygame.time.Clock()
        self.sprites = _carregar_sprites_selecao()

        self.fonte_titulo  = pygame.font.SysFont("Arial", 52, bold=True)
        self.fonte_sub     = pygame.font.SysFont("Arial", 28)
        self.fonte_label   = pygame.font.SysFont("Arial", 22, bold=True)
        self.fonte_pequena = pygame.font.SysFont("Arial", 18)

        self.n_jogadores = 2
        self.jogador_foco = 0 # Jogador que está escolhendo no momento
        self.configs = [{"nome_input": None, "personagem": None} for _ in range(MAX_JOGADORES)]
        self._construir_ui()

    def _construir_ui(self):
        PAINEL_W = 420
        GAP      = 30
        total_w  = self.n_jogadores * PAINEL_W + (self.n_jogadores - 1) * GAP
        start_x  = (LARGURA - total_w) // 2
        INPUT_Y  = 200

        # Ajusta inputs de texto baseados no número de jogadores ativos
        for i in range(MAX_JOGADORES):
            if i < self.n_jogadores:
                ix = start_x + i * (PAINEL_W + GAP) + 10
                if self.configs[i]["nome_input"] is None:
                    self.configs[i]["nome_input"] = InputTexto(ix, INPUT_Y, PAINEL_W - 20, 46, placeholder=f"Jogador {i + 1}")
                else:
                    self.configs[i]["nome_input"].rect.x = ix
            else:
                self.configs[i]["nome_input"] = None
                self.configs[i]["personagem"] = None

        if self.jogador_foco >= self.n_jogadores:
            self.jogador_foco = self.n_jogadores - 1

        self.btn_menos = Botao(LARGURA // 2 - 160, 120, 60, 46, "−", DOURADO_ESC)
        self.btn_mais  = Botao(LARGURA // 2 +  90, 120, 60, 46, "+", DOURADO_ESC)

        # Fileira ÚNICA de personagens centralizada na parte inferior
        CARD_W   = SPRITE_W + 20
        GRID_GAP = 16
        grid_total = N_PERSONAGENS * CARD_W + (N_PERSONAGENS - 1) * GRID_GAP
        grid_start = (LARGURA - grid_total) // 2
        GRID_Y = 480

        self.cards = []
        for j in range(N_PERSONAGENS):
            cx = grid_start + j * (CARD_W + GRID_GAP)
            self.cards.append(BotaoPersonagem(cx, GRID_Y, self.sprites[j], j))

        self.btn_iniciar = Botao(LARGURA // 2 - 150, ALTURA - 110, 300, 60, "▶  INICIAR JOGO")
        self.btn_voltar = Botao(60, ALTURA - 110, 200, 60, "← Voltar", CINZA)

    def _personagem_usado_por(self, p_idx: int) -> tuple[str | None, int | None]:
        """Retorna quem escolheu o personagem (Nome, Index do jogador)."""
        for i in range(self.n_jogadores):
            if self.configs[i]["personagem"] == p_idx + 1:
                inp = self.configs[i]["nome_input"]
                return (inp.texto if inp and inp.texto.strip() else f"Jogador {i+1}"), i
        return None, None

    def _pode_iniciar(self) -> tuple[bool, str]:
        for i in range(self.n_jogadores):
            inp = self.configs[i]["nome_input"]
            if not inp or not inp.texto.strip():
                return False, f"Digite o nome do Jogador {i + 1}"
            if self.configs[i]["personagem"] is None:
                return False, f"O {inp.texto.strip()} não escolheu um personagem!"
        return True, ""

    def rodar(self) -> list[dict] | None:
        mensagem_erro = ""
        timer_erro    = 0

        while True:
            dt        = self.clock.tick(60)
            pos_mouse = pygame.mouse.get_pos()

            self.btn_menos.atualizar(pos_mouse)
            self.btn_mais.atualizar(pos_mouse)
            self.btn_iniciar.atualizar(pos_mouse)
            self.btn_voltar.atualizar(pos_mouse)
            
            for card in self.cards:
                card.atualizar(pos_mouse)
                
            for i in range(self.n_jogadores):
                if self.configs[i]["nome_input"]:
                    self.configs[i]["nome_input"].atualizar(dt)

            if timer_erro > 0:
                timer_erro -= dt
            else:
                mensagem_erro = ""

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                for i in range(self.n_jogadores):
                    if self.configs[i]["nome_input"]:
                        self.configs[i]["nome_input"].evento(event)
                        if self.configs[i]["nome_input"].ativo:
                            self.jogador_foco = i

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    pos = event.pos

                    if self.btn_menos.clicado(pos) and self.n_jogadores > MIN_JOGADORES:
                        self.n_jogadores -= 1
                        self._construir_ui()
                        continue

                    if self.btn_mais.clicado(pos) and self.n_jogadores < MAX_JOGADORES:
                        self.n_jogadores += 1
                        self._construir_ui()
                        continue

                    # Clique nos cards de Personagens
                    for j, card in enumerate(self.cards):
                        if card.clicado(pos):
                            dono_nome, dono_idx = self._personagem_usado_por(j)
                            # Se ninguém escolheu ou se foi o jogador atual trocando
                            if dono_idx is None or dono_idx == self.jogador_foco:
                                self.configs[self.jogador_foco]["personagem"] = j + 1
                            else:
                                mensagem_erro = f"Personagem já escolhido por {dono_nome}!"
                                timer_erro = 2000

                    if self.btn_iniciar.clicado(pos):
                        ok, msg = self._pode_iniciar()
                        if ok:
                            return [
                                {
                                    "nome": self.configs[i]["nome_input"].texto.strip(),
                                    "personagem": self.configs[i]["personagem"]
                                }
                                for i in range(self.n_jogadores)
                            ]
                        else:
                            mensagem_erro = msg
                            timer_erro    = 3000

                    if self.btn_voltar.clicado(pos):
                        return None

            # ── DRAW ──────────────────────────────────────────────────────
            self.tela.fill(FUNDO)

            # Título
            titulo = self.fonte_titulo.render("TECHNOPOLY", True, DOURADO)
            self.tela.blit(titulo, (LARGURA // 2 - titulo.get_width() // 2, 32))
            sub = self.fonte_sub.render("Configuração de Jogadores", True, CINZA)
            self.tela.blit(sub, (LARGURA // 2 - sub.get_width() // 2, 96))

            # Controle de quantidade de jogadores
            n_label = self.fonte_label.render(f"Jogadores:   {self.n_jogadores}", True, BRANCO)
            self.tela.blit(n_label, (LARGURA // 2 - 100, 132))
            self.btn_menos.desenhar(self.tela)
            self.btn_mais.desenhar(self.tela)

            # Desenha os Painéis Superiores (Inputs dos nomes)
            PAINEL_W = 420
            GAP      = 30
            total_w  = self.n_jogadores * PAINEL_W + (self.n_jogadores - 1) * GAP
            start_x  = (LARGURA - total_w) // 2

            for i in range(self.n_jogadores):
                px = start_x + i * (PAINEL_W + GAP)
                
                # Se for o painel em foco, destaca a cor
                cor_label = DOURADO if i == self.jogador_foco else CINZA
                marcador_foco = "➔ " if i == self.jogador_foco else ""
                
                lbl = self.fonte_label.render(f"{marcador_foco}Jogador {i + 1}", True, cor_label)
                self.tela.blit(lbl, (px + 10, 172))
                
                inp = self.configs[i]["nome_input"]
                if inp:
                    inp.desenhar(self.tela)
                
                # Texto indicando o personagem selecionado abaixo do input
                p_num = self.configs[i]["personagem"]
                p_texto = f"Personagem P{p_num}" if p_num else "Nenhum escolhido"
                lbl_p = self.fonte_pequena.render(p_texto, True, DOURADO if p_num else VERMELHO)
                self.tela.blit(lbl_p, (px + 15, 255))

            # Divisor visual entre os nomes e a galeria de seleção
            pygame.draw.line(self.tela, (40, 35, 20), (100, 320), (LARGURA - 100, 320), 2)

            # Título da Galeria de Personagens
            msg_foco = f"Selecione o Personagem do Jogador {self.jogador_foco + 1}:"
            lbl_galeria = self.fonte_sub.render(msg_foco, True, DOURADO)
            self.tela.blit(lbl_galeria, (LARGURA // 2 - lbl_galeria.get_width() // 2, 360))

            # Renderiza a Fileira Única de Cards
            for j, card in enumerate(self.cards):
                dono_nome, dono_idx = self._personagem_usado_por(j)
                selecionado_por_mim = (dono_idx == self.jogador_foco)
                card.desenhar(self.tela, dono_nome, selecionado_por_mim)

            # Mensagens de Erro/Validação
            if mensagem_erro:
                err = self.fonte_label.render(mensagem_erro, True, VERMELHO)
                self.tela.blit(err, (LARGURA // 2 - err.get_width() // 2, ALTURA - 155))

            self.btn_iniciar.desenhar(self.tela)
            self.btn_voltar.desenhar(self.tela)

            pygame.display.flip()