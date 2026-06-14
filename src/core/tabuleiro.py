# src/core/tabuleiro.py
from src.core.propriedade import Propriedade, TipoCasa, CorGrupo
from typing import Optional


def construir_tabuleiro() -> list[Propriedade]:
    
    casas = [
        Propriedade(
            0,
            "Partida",
            TipoCasa.INICIO
        ),
        
        Propriedade(
            1, "Shenzhen", TipoCasa.PROPRIEDADE,
            CorGrupo.LARANJA,
            520, 52,
            [260, 780, 2100, 3800, 4700],
            200,
            260
        ),

        Propriedade(
            2, "Porto Alegre", TipoCasa.PROPRIEDADE,
            CorGrupo.ROXO,
            140, 14,
            [70, 210, 550, 1000, 1400],
            50,
            70
        ),

        Propriedade(
            3, "Barcelona", TipoCasa.PROPRIEDADE,
            CorGrupo.ROSA,
            400, 40,
            [200, 600, 1500, 2600, 3400],
            150,
            200
        ),

        Propriedade(
            4, "Curitiba", TipoCasa.PROPRIEDADE,
            CorGrupo.ROXO,
            120, 12,
            [60, 180, 500, 900, 1300],
            50,
            60
        ),

        Propriedade(
            5, "Dublin", TipoCasa.PROPRIEDADE,
            CorGrupo.AZUL,
            280, 28,
            [140, 420, 950, 1700, 2400],
            100,
            140
        ),

        Propriedade(6, "Zona Neutra", TipoCasa.NADA),

        Propriedade(
            7, "Nova York", TipoCasa.PROPRIEDADE,
            CorGrupo.VERMELHO,
            600, 60,
            [300, 900, 2500, 4600, 5500],
            250,
            300
        ),

        Propriedade(
            8, "Campinas", TipoCasa.PROPRIEDADE,
            CorGrupo.ROXO,
            100, 10,
            [50, 150, 450, 800, 1200],
            50,
            50
        ),

        Propriedade(9, "Vá Para Prisão", TipoCasa.IR_PARA_PRISAO),

        # BASE

        Propriedade(
            10, "Mônaco", TipoCasa.PROPRIEDADE,
            CorGrupo.AMARELO,
            760, 76,
            [380, 1140, 3400, 6400, 7400],
            300,
            380
        ),

        Propriedade(
            11, "Intel", TipoCasa.PROPRIEDADE,
            CorGrupo.AZUL,
            320, 32,
            [160, 480, 1100, 1900, 2600],
            100,
            160
        ),

        Propriedade(
            12, "Taipei", TipoCasa.PROPRIEDADE,
            CorGrupo.LARANJA,
            480, 48,
            [240, 720, 1900, 3400, 4200],
            200,
            240
        ),

        Propriedade(
            13, "Vancouver", TipoCasa.PROPRIEDADE,
            CorGrupo.AZUL,
            240, 24,
            [120, 360, 850, 1500, 2000],
            100,
            120
        ),

        Propriedade(
            14, "Berlim", TipoCasa.PROPRIEDADE,
            CorGrupo.ROSA,
            360, 36,
            [180, 540, 1300, 2200, 3000],
            150,
            180
        ),

        Propriedade(
            15, "Tóquio", TipoCasa.PROPRIEDADE,
            CorGrupo.VERMELHO,
            660, 66,
            [330, 990, 2800, 5200, 6100],
            250,
            330
        ),

        Propriedade(16, "Sorte", TipoCasa.SORTE),

        Propriedade(
            17, "Belo Horizonte", TipoCasa.PROPRIEDADE,
            CorGrupo.ROXO,
            180, 18,
            [90, 270, 650, 1200, 1700],
            50,
            90
        ),

        Propriedade(
            18, "Hong Kong", TipoCasa.PROPRIEDADE,
            CorGrupo.LARANJA,
            460, 46,
            [230, 690, 1800, 3200, 4000],
            200,
            230
        ),

        Propriedade(
            19, "Paris", TipoCasa.PROPRIEDADE,
            CorGrupo.VERMELHO,
            620, 62,
            [310, 930, 2600, 4800, 5700],
            250,
            310
        ),

        # ESQUERDA

        Propriedade(20, "Férias", TipoCasa.FERIAS),

        Propriedade(
            21, "Dubai", TipoCasa.PROPRIEDADE,
            CorGrupo.AMARELO,
            720, 72,
            [360, 1080, 3200, 6000, 7000],
            300,
            360
        ),

        Propriedade(
            22, "Seattle", TipoCasa.PROPRIEDADE,
            CorGrupo.LARANJA,
            500, 50,
            [250, 750, 2000, 3600, 4500],
            200,
            250
        ),

        Propriedade(
            23, "Recife", TipoCasa.PROPRIEDADE,
            CorGrupo.ROXO,
            160, 16,
            [80, 240, 600, 1100, 1500],
            50,
            80
        ),

        Propriedade(
            24, "Amsterdã", TipoCasa.PROPRIEDADE,
            CorGrupo.ROSA,
            380, 38,
            [190, 570, 1400, 2400, 3200],
            150,
            190
        ),

        Propriedade(
            25, "Nvidia", TipoCasa.PROPRIEDADE,
            CorGrupo.AZUL,
            340, 34,
            [170, 510, 1200, 2100, 2800],
            100,
            170
        ),

        Propriedade(
            26, "Singapura", TipoCasa.PROPRIEDADE,
            CorGrupo.ROSA,
            420, 42,
            [210, 630, 1600, 2800, 3600],
            150,
            210
        ),

        Propriedade(
            27, "Estocolmo", TipoCasa.PROPRIEDADE,
            CorGrupo.AZUL,
            300, 30,
            [150, 450, 1000, 1800, 2500],
            100,
            150
        ),

        Propriedade(
            28, "Londres", TipoCasa.PROPRIEDADE,
            CorGrupo.VERMELHO,
            580, 58,
            [290, 870, 2400, 4400, 5300],
            250,
            290
        ),

        # TOPO

        Propriedade(29, "Prisão", TipoCasa.PRISAO),

        Propriedade(30, "Zona Neutra", TipoCasa.NADA),

        Propriedade(
            31, "Xangai", TipoCasa.PROPRIEDADE,
            CorGrupo.VERMELHO,
            640, 64,
            [320, 960, 2700, 5000, 5900],
            250,
            320
        ),

        Propriedade(
            32, "Toronto", TipoCasa.PROPRIEDADE,
            CorGrupo.AZUL,
            220, 22,
            [110, 330, 800, 1400, 1900],
            100,
            110
        ),

        Propriedade(
            33, "Tel Aviv", TipoCasa.PROPRIEDADE,
            CorGrupo.ROSA,
            340, 34,
            [170, 510, 1200, 2100, 2800],
            150,
            170
        ),

        Propriedade(
            34, "Zurique", TipoCasa.PROPRIEDADE,
            CorGrupo.AMARELO,
            800, 80,
            [400, 1200, 3600, 6800, 7800],
            300,
            400
        ),

        Propriedade(
            35, "Seul", TipoCasa.PROPRIEDADE,
            CorGrupo.LARANJA,
            540, 54,
            [270, 810, 2200, 4000, 4900],
            200,
            270
        ),

        Propriedade(36, "Sorte", TipoCasa.SORTE),

        Propriedade(
            37, "Vale do Sílicio", TipoCasa.PROPRIEDADE,
            CorGrupo.AMARELO,
            1000, 100,
            [500, 1500, 5000, 9000, 12000],
            400,
            500
        ),

        Propriedade(
            38, "Austin", TipoCasa.PROPRIEDADE,
            CorGrupo.AZUL,
            260, 26,
            [130, 390, 900, 1600, 2200],
            100,
            130
        ),

        Propriedade(
            39, "San Francisco", TipoCasa.PROPRIEDADE,
            CorGrupo.AMARELO,
            850, 85,
            [425, 1275, 3900, 7200, 8300],
            350,
            425
        )]
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