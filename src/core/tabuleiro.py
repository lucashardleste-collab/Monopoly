# src/core/tabuleiro.py
from src.core.propriedade import Propriedade, TipoCasa, CorGrupo
from typing import Optional


def construir_tabuleiro() -> list[Propriedade]:

    casas = [

    Propriedade(0, "Partida", TipoCasa.INICIO),

    # DIREITA DESCENDO
    Propriedade(1, "Shenzhen", TipoCasa.PROPRIEDADE),
    Propriedade(2, "Porto Alegre", TipoCasa.PROPRIEDADE),
    Propriedade(3, "Barcelona", TipoCasa.PROPRIEDADE),
    Propriedade(4, "Curitiba", TipoCasa.PROPRIEDADE),
    Propriedade(5, "Dublin", TipoCasa.PROPRIEDADE),
    Propriedade(6, "Zona Neutra", TipoCasa.AZAR),
    Propriedade(7, "Nova York", TipoCasa.PROPRIEDADE),
    Propriedade(8, "Campinas", TipoCasa.PROPRIEDADE),

    Propriedade(9, "Vá Para Prisão", TipoCasa.IR_PARA_PRISAO),

    # BASE INDO PARA ESQUERDA
    Propriedade(10, "Mônaco", TipoCasa.PROPRIEDADE),
    Propriedade(11, "Intel", TipoCasa.PROPRIEDADE),
    Propriedade(12, "Taipei", TipoCasa.PROPRIEDADE),
    Propriedade(13, "Vancouver", TipoCasa.PROPRIEDADE),
    Propriedade(14, "Berlim", TipoCasa.PROPRIEDADE),
    Propriedade(15, "Tóquio", TipoCasa.PROPRIEDADE),
    Propriedade(16, "Sorte", TipoCasa.SORTE),
    Propriedade(17, "Belo Horizonte", TipoCasa.PROPRIEDADE),
    Propriedade(18, "Hong Kong", TipoCasa.PROPRIEDADE),

    Propriedade(19, "Férias", TipoCasa.FERIAS),

    # ESQUERDA SUBINDO
    Propriedade(20, "Dubai", TipoCasa.PROPRIEDADE),
    Propriedade(21, "Seattle", TipoCasa.PROPRIEDADE),
    Propriedade(22, "Recife", TipoCasa.PROPRIEDADE),
    Propriedade(23, "Amsterdã", TipoCasa.PROPRIEDADE),
    Propriedade(24, "Nvidia", TipoCasa.PROPRIEDADE),
    Propriedade(25, "Singapura", TipoCasa.PROPRIEDADE),
    Propriedade(26, "Estocolmo", TipoCasa.PROPRIEDADE),
    Propriedade(27, "Londres", TipoCasa.PROPRIEDADE),

    Propriedade(28, "Prisão", TipoCasa.PRISAO),

    # TOPO INDO PARA DIREITA
    Propriedade(29, "Zona Neutra", TipoCasa.AZAR),
    Propriedade(30, "Xangai", TipoCasa.PROPRIEDADE),
    Propriedade(31, "Toronto", TipoCasa.PROPRIEDADE),
    Propriedade(32, "Tel Aviv", TipoCasa.PROPRIEDADE),
    Propriedade(33, "Zurique", TipoCasa.PROPRIEDADE),
    Propriedade(34, "Seul", TipoCasa.PROPRIEDADE),
    Propriedade(35, "Sorte", TipoCasa.SORTE),
    Propriedade(36, "Vale do Silício", TipoCasa.PROPRIEDADE),
    Propriedade(37, "Austin", TipoCasa.PROPRIEDADE),
    Propriedade(38, "San Francisco", TipoCasa.PROPRIEDADE),

    Propriedade(39, "San Francisco", TipoCasa.PROPRIEDADE),
    ]

    return casas

class Tabuleiro:
    """
    Wrapper do tabuleiro que expõe operações de consulta.
    A lista de casas é a fonte da verdade — essa classe só facilita o acesso.
    """

    def __init__(self):
        self.casas = construir_tabuleiro()
        self.total = len(self.casas)

    def get_casa(self, posicao: int) -> Propriedade:
        """Acesso circular — nunca vai lançar IndexError."""
        return self.casas[posicao % self.total]

    def calcular_nova_posicao(self, posicao_atual: int, passos: int) -> int:
        """
        RF-006/3: Aritmética modular para tabuleiro circular.
        Simples assim. Não precisa de mais nada aqui.
        """
        return (posicao_atual + passos) % self.total

    def passou_pelo_inicio(self, pos_antiga: int, pos_nova: int) -> bool:
        """
        RF-007/3: Detecta se o jogador cruzou a casa 0 (Início).
        O único edge case: se pos_nova < pos_antiga, houve wrap-around.
        """
        return pos_nova < pos_antiga

    def get_propriedades_da_cor(self, cor: CorGrupo) -> list[Propriedade]:
        """RF-009/5: Retorna todas as propriedades de um grupo de cor."""
        return [c for c in self.casas if c.cor == cor]

    def __repr__(self) -> str:
        return f"Tabuleiro com {self.total} casas"