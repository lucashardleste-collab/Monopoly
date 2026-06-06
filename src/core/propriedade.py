# src/core/propriedade.py
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class TipoCasa(Enum):
    """
    Define o 'contrato' de comportamento de cada casa.
    Usando Enum em vez de strings soltas para evitar bugs de typo.
    ("prisao" vs "Prisao" vs "PRISAO" — já vi isso quebrar sistema em prod.)
    """
    INICIO = "inicio"
    PROPRIEDADE = "propriedade"
    PRISAO = "prisao"
    FERIAS = "ferias"          # Só de passagem (visita) ou preso
    IR_PARA_PRISAO = "ir_para_prisao"
    SORTE = "sorte"
    AZAR = "azar"
    IMPOSTO = "imposto"


class CorGrupo(Enum):
    """
    Grupos de cor do tabuleiro — base para verificação de monopólio (RF-009/5).
    """
    ROXO = "roxo"
    CIANO = "ciano"
    ROSA = "rosa"
    LARANJA = "laranja"
    VERMELHO = "vermelho"
    AMARELO = "amarelo"
    VERDE = "verde"
    AZUL = "azul"
    ESTACAO = "estacao"        # Estações de trem
    SERVICO = "servico"        # Companhias (luz, água)


@dataclass
class Propriedade:
    """
    Representa UMA casa do tipo comprável no tabuleiro.

    Usamos @dataclass para não escrever __init__ boilerplate.
    Todos os atributos de estado mutável ficam aqui, centralizados.
    """
    # --- Atributos Imutáveis (definidos na criação do tabuleiro) ---
    id: int
    nome: str
    tipo: TipoCasa
    cor: Optional[CorGrupo] = None       # None para casas especiais

    preco: int = 0                        # Custo de compra
    aluguel_base: int = 0                 # Aluguel sem construção
    aluguel_por_andar: list = field(default_factory=list)
    # Ex: [50, 150, 450, 625, 750] → aluguel com 1, 2, 3, 4 andares
    preco_andar: int = 0                  # Custo por andar construído
    valor_hipoteca: int = 0               # Quanto o banco paga na hipoteca

    # --- Atributos de Estado (mudam durante o jogo) ---
    dono_id: Optional[int] = None         # ID do jogador dono
    hipotecada: bool = False
    andares: int = 0                      # Qtd de andares construídos (0-4 = casas, 5 = hotel)

    def esta_disponivel(self) -> bool:
        """Propriedade pode ser comprada?"""
        return self.dono_id is None and not self.hipotecada

    def calcular_aluguel(self) -> int:
        """
        Retorna o aluguel atual baseado nos andares construídos.
        Se hipotecada, não cobra nada — regra oficial do Monopoly.
        """
        if self.hipotecada:
            return 0
        if self.andares == 0:
            return self.aluguel_base
        # andares vai de 1 a 5 (5 = hotel)
        return self.aluguel_por_andar[self.andares - 1]

    def __repr__(self) -> str:
        status = f"Dono ID:{self.dono_id}" if self.dono_id else "Disponível"
        return f"[{self.nome} | {status} | Andares: {self.andares}]"