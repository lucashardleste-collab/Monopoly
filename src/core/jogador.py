# src/core/jogador.py
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Jogador:
    """
    Entidade central do jogo.

    DECISÃO: saldo_inicial como constante separada para facilitar
    reset em testes e futuras partidas sem instanciar tudo de novo.
    """
    id: int
    nome: str
    saldo: int = 1500               # Saldo padrão do Monopoly
    posicao: int = 0                # Começa no Início (casa 0)
    ativo: bool = True              # False = falido, saiu do jogo

    # Propriedades que o jogador possui (lista de IDs das casas)
    propriedades: list[int] = field(default_factory=list)

    # Controle de prisão
    preso: bool = False
    turnos_preso: int = 0           # Conta tentativas de sair (max 3)
    tem_cartao_sair_prisao: bool = False

    def esta_ativo(self) -> bool:
        return self.ativo

    def pode_comprar(self, preco: int) -> bool:
        """Validação simples — saldo cobre o preço?"""
        return self.saldo >= preco

    def receber(self, valor: int, motivo: str = "") -> None:
        """
        Todo crédito passa aqui.
        O parâmetro 'motivo' é só para o log — facilita muito o debug.
        ("Por que esse cara tem R$99999?" — o log responde.)
        """
        if valor < 0:
            raise ValueError(f"Use debitar() para valores negativos. Valor: {valor}")
        self.saldo += valor
        if motivo:
            print(f"  💰 {self.nome} recebeu ${valor} ({motivo}). Saldo: ${self.saldo}")

    def debitar(self, valor: int, motivo: str = "") -> bool:
        """
        Todo débito passa aqui.
        Retorna False se saldo ficar negativo — sinaliza crise financeira
        para a máquina de estados (RF-013/7) sem lançar exceção.

        POR QUE não lançar exceção?
        Saldo negativo no Monopoly não é erro — é um estado válido
        que dispara o fluxo de hipoteca. Exceção seria semântica errada.
        """
        if valor < 0:
            raise ValueError(f"Valor de débito deve ser positivo. Valor: {valor}")
        self.saldo -= valor
        if motivo:
            print(f"  💸 {self.nome} pagou ${valor} ({motivo}). Saldo: ${self.saldo}")
        return self.saldo >= 0      # False = entrou em crise

    def mover(self, passos: int, total_casas: int) -> tuple[int, bool]:
        """
        RF-006/3 + RF-007/3: Move o jogador e detecta passagem pelo Início.
        Retorna (nova_posicao, passou_pelo_inicio).

        DECISÃO: a lógica de bônus ($200) NÃO fica aqui.
        Jogador não sabe de dinheiro de passagem — isso é responsabilidade
        do motor de transações. SRP em ação.
        """
        pos_antiga = self.posicao
        self.posicao = (self.posicao + passos) % total_casas
        passou_inicio = self.posicao < pos_antiga or (pos_antiga != 0 and self.posicao == 0)
        return self.posicao, passou_inicio

    def adicionar_propriedade(self, casa_id: int) -> None:
        if casa_id not in self.propriedades:
            self.propriedades.append(casa_id)

    def remover_propriedade(self, casa_id: int) -> None:
        if casa_id in self.propriedades:
            self.propriedades.remove(casa_id)

    def entrar_na_prisao(self) -> None:
        """RF-012/6 + IR_PARA_PRISAO: centraliza a lógica de prisão."""
        self.preso = True
        self.turnos_preso = 0
        self.posicao = 10           # Casa da Prisão é sempre a 10
        print(f"  🚔 {self.nome} foi preso!")

    def tentar_sair_prisao(self, tirou_duplo: bool) -> bool:
        """
        Retorna True se conseguiu sair.
        Regra: sai com duplo nos dados OU após 3 tentativas (paga multa).
        A multa em si é processada em transacoes.py.
        """
        self.turnos_preso += 1
        if tirou_duplo or self.tem_cartao_sair_prisao:
            self.preso = False
            self.turnos_preso = 0
            self.tem_cartao_sair_prisao = False
            return True
        if self.turnos_preso >= 3:
            self.preso = False
            self.turnos_preso = 0
            return True             # Sai, mas vai pagar multa em transacoes.py
        return False

    def declarar_falencia(self) -> None:
        """RF-015/7: Marca jogador como inativo."""
        self.ativo = False
        print(f"  💀 {self.nome} declarou falência e saiu do jogo.")

    def __repr__(self) -> str:
        status = "🔒 Preso" if self.preso else f"📍 Casa {self.posicao}"
        return (f"[{self.nome} | Saldo: ${self.saldo} | "
                f"{status} | Propriedades: {len(self.propriedades)}]")