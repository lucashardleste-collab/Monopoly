# main.py
from src.core.game import Monopoly


def main():
    print("═" * 55)
    print("  Bem-vindo ao Banco Imobiliário!")
    print("═" * 55)

    nomes = []
    qtd = int(input("\n  Quantos jogadores? (2-6) › "))

    for i in range(qtd):
        nome = input(f"  Nome do jogador {i + 1} › ").strip()
        nomes.append(nome or f"Jogador {i + 1}")

    jogo = Monopoly(nomes_jogadores=nomes)
    jogo.iniciar()


if __name__ == "__main__":
    main()