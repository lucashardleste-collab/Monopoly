# src/core/dados.py
import random
from dataclasses import dataclass


@dataclass
class ResultadoDados:
    """
    Resultado de um lançamento.
    Separar em dataclass evita ficar passando tuplas soltas pelo código.
    ('O que era o índice 0 mesmo?' — nunca mais.)
    """
    dado1: int
    dado2: int

    @property
    def total(self) -> int:
        return self.dado1 + self.dado2

    @property
    def eh_duplo(self) -> bool:
        """Duplo = ambos os dados com mesmo valor. Relevante para prisão."""
        return self.dado1 == self.dado2

    def __repr__(self) -> str:
        duplo = " 🎯 DUPLO!" if self.eh_duplo else ""
        return f"[🎲 {self.dado1} + {self.dado2} = {self.total}{duplo}]"


class Dados:
    """
    Isolamos o random aqui por um motivo prático:
    nos testes, trocamos o random por valores fixos (mock)
    sem tocar em nenhuma outra classe.

    Ex: forçar duplo para testar prisão, ou forçar 7 para
    testar passagem pelo Início. Sem isso, fica impossível
    de testar deterministicamente.
    """

    def __init__(self, seed: int = None):
        """
        seed opcional — útil para testes reproduzíveis.
        dados = Dados(seed=42) → sempre o mesmo resultado.
        """
        self._rng = random.Random(seed)
        self.historico: list[ResultadoDados] = []
        self._duplos_consecutivos: int = 0

    def rolar(self) -> ResultadoDados:
        """
        RF-005/3: Lança dois dados de 6 faces.

        Regra especial: 3 duplos consecutivos = vai para a prisão.
        Registramos aqui, a ação é tomada em game.py.
        """
        resultado = ResultadoDados(
            dado1=self._rng.randint(1, 6),
            dado2=self._rng.randint(1, 6)
        )
        self.historico.append(resultado)

        if resultado.eh_duplo:
            self._duplos_consecutivos += 1
        else:
            self._duplos_consecutivos = 0

        print(f"  {resultado}")
        return resultado

    def tres_duplos_consecutivos(self) -> bool:
        """Retorna True se o jogador tirou 3 duplos seguidos → prisão."""
        return self._duplos_consecutivos >= 3

    def resetar_duplos(self) -> None:
        """Chamado quando o turno termina ou jogador é preso."""
        self._duplos_consecutivos = 0

    def __repr__(self) -> str:
        return f"Dados | Último: {self.historico[-1] if self.historico else 'Nenhum'}"