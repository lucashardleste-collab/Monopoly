# src/view/tela_menu.py
import pygame
import sys
import os


class TelaMenu:
    def __init__(self):
        pygame.init()

        # 1. Definição da resolução da janela (proporcional à imagem premium)
        self.largura = 1200
        self.altura = 800
        self.tela = pygame.display.set_mode((self.largura, self.altura))
        pygame.display.set_caption("Monopoly Empire - Menu Principal")

        # 2. Carregar a imagem real de fundo (RF-019/9)
        caminho_imagem = os.path.join("images", "Menu_imagem.png")
        try:
            self.imagem_fundo = pygame.image.load(caminho_imagem)
            self.imagem_fundo = pygame.transform.scale(self.imagem_fundo, (self.largura, self.altura))
        except pygame.error:
            print(f"❌ Erro: Não foi possível encontrar a imagem em: {caminho_imagem}")
            print("👉 Certifica-te de que a pasta 'assets/' está na raiz do teu projeto.")
            sys.exit()

        # 3. Definição das áreas dos botões (Colisores/Hitboxes)
        # Retângulos invisíveis posicionados exatamente em cima das caixas da imagem
        # Parâmetros: (X_inicial, Y_inicial, largura, altura)
        self.retangulo_iniciar = pygame.Rect(390, 405, 420, 110)
        self.retangulo_sair = pygame.Rect(390, 520, 420, 110)

        # Controle de efeito visual ao passar o rato (hover)
        self.hover_iniciar = False
        self.hover_sair = False

    def rodar_menu(self) -> str:
        """
        Executa o loop visual do menu.
        Retorna 'INICIAR' se o jogador clicar em Iniciar, ou fecha o programa se clicar em Sair.
        """
        relogio = pygame.time.Clock()

        while True:
            # --- 1. DESENHAR O FUNDO ---
            # Renderiza a tua imagem exata do Monopoly Empire
            self.tela.blit(self.imagem_fundo, (0, 0))

            # --- 2. EFEITO DE HOVER (BORDA DE LUZ ADAPTADA) ---
            # Desenha uma borda dourada fina se o rato estiver em cima do botão
            posicao_rato = pygame.mouse.get_pos()
            self.hover_iniciar = self.retangulo_iniciar.collidepoint(posicao_rato)
            self.hover_sair = self.retangulo_sair.collidepoint(posicao_rato)

            if self.hover_iniciar:
                # Cor Ouro Premium: (214, 160, 0)
                pygame.draw.rect(self.tela, (214, 160, 0), self.retangulo_iniciar, 3, border_radius=15)
            if self.hover_sair:
                pygame.draw.rect(self.tela, (214, 160, 0), self.retangulo_sair, 3, border_radius=15)

            # --- 3. CAPTURA DE EVENTOS DE CLIQUE ---
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if evento.type == pygame.MOUSEBUTTONDOWN:
                    if evento.button == 1:  # Clique esquerdo do rato
                        # Se clicar na caixa do INICIAR
                        if self.retangulo_iniciar.collidepoint(evento.pos):
                            return "INICIAR"

                        # Se clicar na caixa do SAIR
                        elif self.retangulo_sair.collidepoint(evento.pos):
                            pygame.quit()
                            sys.exit()

            pygame.display.flip()
            relogio.tick(60)  # Limita a 60 FPS


# ─── BLOCO DE INICIALIZAÇÃO DIRETA ───
if __name__ == "__main__":
    # Instancia a classe que criaste acima
    menu = TelaMenu()

    print("🖥️ Inicializando a janela gráfica do Pygame...")

    # Arranca o loop e aguarda o clique
    resultado = menu.rodar_menu()

    if resultado == "INICIAR":
        print("🚀 Sucesso! O botão INICIAR foi detetado. O ecrã do jogo pode ser carregado agora.")
