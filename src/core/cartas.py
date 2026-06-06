# src/core/cartas.py
import random
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Callable, Optional


# ---------------------------------------------------------------------------
# TIPOS DE EFEITO
# ---------------------------------------------------------------------------

class TipoEfeito(Enum):
    """
    Cada carta tem UM efeito principal.
    Separar em enum evita lógica espalhada com ifs em string.
    ("if carta == 'pague 50' or carta == 'Pague 50' or..." — não.)
    """
    RECEBER_BANCO       = auto()   # Jogador recebe $ do banco
    PAGAR_BANCO         = auto()   # Jogador paga $ ao banco
    RECEBER_JOGADORES   = auto()   # Todos os jogadores pagam ao atual
    PAGAR_JOGADORES     = auto()   # Jogador paga $ a cada outro jogador
    MOVER_PARA         = auto()   # Vai para casa específica
    IR_PARA_PRISAO      = auto()   # Vai direto para a prisão
    SAIR_PRISAO         = auto()   # Guarda cartão "saia livre"
    PAGAR_POR_ANDAR     = auto()   # Paga valor * nº de andares construídos


# ---------------------------------------------------------------------------
# ESTRUTURA DE UMA CARTA
# ---------------------------------------------------------------------------

@dataclass
class Carta:
    """
    Representa uma carta de Sorte ou Azar.

    DECISÃO: o efeito é declarativo (dados + tipo) em vez de
    uma função lambda embutida. Isso facilita serialização futura
    para o sistema de Save (RF-019/10) — não dá pra salvar lambdas em JSON.
    """
    descricao: str
    tipo: TipoEfeito
    valor: int = 0              # Valor monetário (quando aplicável)
    casa_destino: int = -1      # Casa alvo para MOVER_PARA (-1 = não se aplica)
    passa_pelo_inicio: bool = True  # Recebe $200 se passar pelo início ao mover?

    def __repr__(self) -> str:
        return f"🃏 [{self.tipo.name}] {self.descricao}"


# ---------------------------------------------------------------------------
# FÁBRICA DAS CARTAS
# ---------------------------------------------------------------------------

def _criar_cartas_sorte() -> list[Carta]:
    """
    Deck de Sorte — efeitos geralmente positivos.
    Baseado no Monopoly clássico adaptado para o Banco Imobiliário BR.
    """
    return [
        Carta(
            descricao="Avance até o Início. Receba $200.",
            tipo=TipoEfeito.MOVER_PARA,
            casa_destino=0,
            passa_pelo_inicio=True
        ),
        Carta(
            descricao="Banco paga dividendos. Receba $50.",
            tipo=TipoEfeito.RECEBER_BANCO,
            valor=50
        ),
        Carta(
            descricao="Seu prédio e empréstimo vencem. Receba $150.",
            tipo=TipoEfeito.RECEBER_BANCO,
            valor=150
        ),
        Carta(
            descricao="Presente de aniversário! Receba $10 de cada jogador.",
            tipo=TipoEfeito.RECEBER_JOGADORES,
            valor=10
        ),
        Carta(
            descricao="Você ganhou um concurso de palavras cruzadas. Receba $100.",
            tipo=TipoEfeito.RECEBER_BANCO,
            valor=100
        ),
        Carta(
            descricao="Reembolso de imposto de renda. Receba $20.",
            tipo=TipoEfeito.RECEBER_BANCO,
            valor=20
        ),
        Carta(
            descricao="Saia da prisão gratuitamente. Guarde este cartão.",
            tipo=TipoEfeito.SAIR_PRISAO,
        ),
        Carta(
            descricao="Avance até a Avenida São João.",
            tipo=TipoEfeito.MOVER_PARA,
            casa_destino=24,           # Ajustar ao tabuleiro final
            passa_pelo_inicio=True
        ),
        Carta(
            descricao="Serviços médicos. Pague $50.",
            tipo=TipoEfeito.PAGAR_BANCO,
            valor=50
        ),
        Carta(
            descricao="Multa por excesso de velocidade. Pague $15.",
            tipo=TipoEfeito.PAGAR_BANCO,
            valor=15
        ),
    ]


def _criar_cartas_azar() -> list[Carta]:
    """
    Deck de Azar — efeitos geralmente negativos ou neutros.
    """
    return [
        Carta(
            descricao="Vá direto para a prisão. Não passe pelo Início.",
            tipo=TipoEfeito.IR_PARA_PRISAO,
            passa_pelo_inicio=False
        ),
        Carta(
            descricao="Reforma geral: pague $25 por andar construído.",
            tipo=TipoEfeito.PAGAR_POR_ANDAR,
            valor=25
        ),
        Carta(
            descricao="Consulta médica. Pague $100.",
            tipo=TipoEfeito.PAGAR_BANCO,
            valor=100
        ),
        Carta(
            descricao="Você foi multado. Pague $15.",
            tipo=TipoEfeito.PAGAR_BANCO,
            valor=15
        ),
        Carta(
            descricao="Pague impostos escolares de $150.",
            tipo=TipoEfeito.PAGAR_BANCO,
            valor=150
        ),
        Carta(
            descricao="É seu aniversário! Pague $10 a cada jogador.",
            tipo=TipoEfeito.PAGAR_JOGADORES,
            valor=10
        ),
        Carta(
            descricao="Volte ao Início.",
            tipo=TipoEfeito.MOVER_PARA,
            casa_destino=0,
            passa_pelo_inicio=False    # Não recebe $200 ao voltar
        ),
        Carta(
            descricao="Reformas em seus imóveis: $40 por andar.",
            tipo=TipoEfeito.PAGAR_POR_ANDAR,
            valor=40
        ),
        Carta(
            descricao="Receba $25 de serviços prestados.",
            tipo=TipoEfeito.RECEBER_BANCO,
            valor=25
        ),
        Carta(
            descricao="Saia da prisão gratuitamente. Guarde este cartão.",
            tipo=TipoEfeito.SAIR_PRISAO,
        ),
    ]


# ---------------------------------------------------------------------------
# DECK — BARALHO JOGÁVEL
# ---------------------------------------------------------------------------

class Deck:
    """
    RF-011/6: Baralho embaralhado com reposição automática.

    DECISÃO: quando o deck acaba, reembaralha em vez de lançar erro.
    Comportamento idêntico ao jogo físico — pilha vazia = reembaralha.
    """

    def __init__(self, cartas: list[Carta], seed: int = None):
        self._originais = cartas[:]          # Cópia imutável de referência
        self._pilha: list[Carta] = []
        self._descartadas: list[Carta] = []
        self._rng = random.Random(seed)      # Seed para testes (igual ao Dados)
        self._embaralhar()

    def _embaralhar(self) -> None:
        """Recolhe descartadas + restantes e embaralha tudo."""
        self._pilha = self._originais[:]
        self._rng.shuffle(self._pilha)
        self._descartadas.clear()

    def sacar(self) -> Carta:
        """
        RF-012/6: Saca a carta do topo.
        Reembaralha automaticamente se o deck estiver vazio.
        Cartas SAIR_PRISAO ficam com o jogador — não são descartadas
        até serem usadas. Essa lógica fica no game.py.
        """
        if not self._pilha:
            print("  🔄 Deck vazio — reembaralhando...")
            self._embaralhar()

        carta = self._pilha.pop()
        self._descartadas.append(carta)
        print(f"  {carta}")
        return carta

    def __len__(self) -> int:
        return len(self._pilha)

    def __repr__(self) -> str:
        return (f"Deck ({len(self._pilha)} restantes, "
                f"{len(self._descartadas)} descartadas)")


# ---------------------------------------------------------------------------
# PROCESSADOR DE EFEITOS
# ---------------------------------------------------------------------------

def aplicar_carta(
    carta: Carta,
    jogador_atual,          # Jogador — import evitado para não criar ciclo
    todos_jogadores: list,
    tabuleiro,
    transacoes_mod          # Passamos o módulo como dependência
) -> dict:
    """
    RF-012/6: Executa o efeito da carta sacada.

    DECISÃO: retorna um dict de resultado em vez de side-effects silenciosos.
    O game.py usa esse dict para decidir a próxima transição de estado.

    Retorno padrão:
    {
        "moveu": bool,
        "nova_posicao": int | None,
        "passa_inicio": bool,
        "preso": bool,
        "crise": bool,
        "cartao_prisao": bool
    }
    """
    resultado = {
        "moveu": False,
        "nova_posicao": None,
        "passa_inicio": False,
        "preso": False,
        "crise": False,
        "cartao_prisao": False
    }

    jogadores_ativos = [j for j in todos_jogadores if j.ativo and j.id != jogador_atual.id]

    # --- RECEBER DO BANCO ---
    if carta.tipo == TipoEfeito.RECEBER_BANCO:
        jogador_atual.receber(carta.valor, motivo=carta.descricao)

    # --- PAGAR AO BANCO ---
    elif carta.tipo == TipoEfeito.PAGAR_BANCO:
        saldo_ok = jogador_atual.debitar(carta.valor, motivo=carta.descricao)
        resultado["crise"] = not saldo_ok

    # --- RECEBER DE CADA JOGADOR ---
    elif carta.tipo == TipoEfeito.RECEBER_JOGADORES:
        for outro in jogadores_ativos:
            saldo_ok = outro.debitar(carta.valor, motivo=f"Pagamento a {jogador_atual.nome}")
            jogador_atual.receber(carta.valor, motivo=f"Recebido de {outro.nome}")
            # Se outro jogador entrar em crise, game.py resolve depois
            # Não interrompemos o loop — todos pagam primeiro

    # --- PAGAR A CADA JOGADOR ---
    elif carta.tipo == TipoEfeito.PAGAR_JOGADORES:
        for outro in jogadores_ativos:
            saldo_ok = jogador_atual.debitar(carta.valor, motivo=f"Pagamento a {outro.nome}")
            outro.receber(carta.valor, motivo=f"Recebido de {jogador_atual.nome}")
            if not saldo_ok:
                resultado["crise"] = True
                break              # Entrou em crise — para aqui, game.py assume

    # --- IR PARA PRISÃO ---
    elif carta.tipo == TipoEfeito.IR_PARA_PRISAO:
        jogador_atual.entrar_na_prisao()
        resultado["preso"] = True
        resultado["moveu"] = True
        resultado["nova_posicao"] = 10

    # --- MOVER PARA CASA ESPECÍFICA ---
    elif carta.tipo == TipoEfeito.MOVER_PARA:
        pos_antiga = jogador_atual.posicao
        jogador_atual.posicao = carta.casa_destino
        resultado["moveu"] = True
        resultado["nova_posicao"] = carta.casa_destino
        resultado["passa_inicio"] = (
            carta.passa_pelo_inicio and carta.casa_destino < pos_antiga
        )
        if resultado["passa_inicio"]:
            transacoes_mod.processar_inicio(jogador_atual)

    # --- SAIR DA PRISÃO ---
    elif carta.tipo == TipoEfeito.SAIR_PRISAO:
        jogador_atual.tem_cartao_sair_prisao = True
        resultado["cartao_prisao"] = True
        print(f"  🎫 {jogador_atual.nome} guardou o cartão 'Saia da Prisão'!")

    # --- PAGAR POR ANDAR ---
    elif carta.tipo == TipoEfeito.PAGAR_POR_ANDAR:
        total_andares = sum(
            tabuleiro.get_casa(pid).andares
            for pid in jogador_atual.propriedades
        )
        total_devido = carta.valor * total_andares
        if total_devido > 0:
            saldo_ok = jogador_atual.debitar(
                total_devido,
                motivo=f"{carta.descricao} ({total_andares} andares × ${carta.valor})"
            )
            resultado["crise"] = not saldo_ok
        else:
            print(f"  ℹ️  {jogador_atual.nome} não tem andares. Sem cobrança.")

    return resultado