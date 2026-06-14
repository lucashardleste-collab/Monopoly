# main.py
import sys
import os

# 1. Ajusta os caminhos primeiro
ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, ROOT_DIR)

# 2. INICIALIZA O PYGAME AQUI, ANTES DOS IMPORTS DE TELAS!
import pygame
pygame.init() 

# 3. Agora os imports podem acontecer com segurança
from src.view.tela_menu import TelaMenu
from src.view.tela_selecao import TelaSelecao
from src.view.tela_jogo import executar_jogo

# ... resto da sua main ...
def main():
    pygame.init()
    
    # 1. Instancia e roda o Menu Inicial
    menu = TelaMenu()
    print("🖥️ Menu Principal aberto...")
    resultado_menu = menu.rodar_menu()
    
    if resultado_menu == "INICIAR":
        # 2. Se o jogador clicou em Iniciar, abre a Tela de Seleção Customizada
        # Passamos a própria tela do menu para economizar recursos e evitar recriar janelas
        print("👥 Abrindo a seleção de personagens...")
        tela_selecao = TelaSelecao(menu.tela)
        lista_jogadores = tela_selecao.rodar()
        
        # Se ele não clicou em voltar e configurou tudo certo
        if lista_jogadores:
            print(f"🎮 Jogadores configurados: {lista_jogadores}")
            # 3. Dispara a tela do tabuleiro passando a lista dinâmica de players!
            executar_jogo(lista_jogadores)
        else:
            print("↩️ Usuário voltou ao menu ou fechou.")
            
if __name__ == "__main__":
    main()