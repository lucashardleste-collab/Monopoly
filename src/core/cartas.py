"""
src/core/cartas.py
==================
Módulo responsável pelas cartas de Sorte e Azar do Banco Imobiliário BR.

Numeração real das imagens
--------------------------
  Sorte : carta_sorte_01 … carta_sorte_08, carta_sorte_19, carta_sorte_20
  Azar  : carta_azar_09  … carta_azar_18

Estrutura de pasta esperada:
    assets/cartas/carta_sorte_01.png  (e demais)
    assets/cartas/carta_azar_09.png   (e demais)

No terminal, cada carta sacada exibe um frame ASCII com o texto e o
caminho da imagem. Ao migrar para interface gráfica, troque
_exibir_imagem_terminal() por uma chamada ao renderer visual.
"""

import os
import random
from dataclasses import dataclass
from enum import Enum, auto


# ---------------------------------------------------------------------------
# CAMINHO BASE DAS IMAGENS
# Relativo à raiz do projeto (dois níveis acima deste arquivo).
# ---------------------------------------------------------------------------

_RAIZ_PROJETO = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")
)
_PASTA_IMAGENS = os.path.join(_RAIZ_PROJETO, "assets", "cartas")


# ---------------------------------------------------------------------------
# TIPOS DE EFEITO
# ---------------------------------------------------------------------------

class TipoEfeito(Enum):
    RECEBER_BANCO       = auto()   # Jogador recebe $ do banco
    PAGAR_BANCO         = auto()   # Jogador paga $ ao banco
    RECEBER_JOGADORES   = auto()   # Todos os outros pagam ao jogador atual
    PAGAR_JOGADORES     = auto()   # Jogador paga $ a cada outro jogador
    MOVER_PARA          = auto()   # Vai para casa específica
    IR_PARA_PRISAO      = auto()   # Vai direto para a prisão
    SAIR_PRISAO         = auto()   # Guarda cartão "saia livre"
    PAGAR_POR_ANDAR     = auto()   # Paga valor × nº de andares construídos


# ---------------------------------------------------------------------------
# ESTRUTURA DE UMA CARTA
# ---------------------------------------------------------------------------

@dataclass
class Carta:
    """
    Representa uma carta de Sorte ou Azar.

    O efeito é declarativo (dados + TipoEfeito) em vez de lambda —
    facilita serialização para Save (RF-019/10).

    Parâmetros
    ----------
    descricao        : Texto exibido ao jogador.
    tipo             : Efeito a aplicar (TipoEfeito).
    valor            : Quantia monetária (0 quando não aplicável).
    casa_destino     : Índice da casa-alvo para MOVER_PARA (-1 = N/A).
    passa_pelo_inicio: True → recebe $200 se passar pela casa 0.
    imagem           : Caminho do PNG relativo à raiz do projeto.
    """
    descricao: str
    tipo: TipoEfeito
    valor: int = 0
    casa_destino: int = -1
    passa_pelo_inicio: bool = True
    imagem: str = ""

    def __repr__(self) -> str:
        return f"🃏 [{self.tipo.name}] {self.descricao}"


# ---------------------------------------------------------------------------
# EXIBIÇÃO NO TERMINAL
# ---------------------------------------------------------------------------

def _exibir_imagem_terminal(carta: Carta) -> None:
    """
    Exibe um frame ASCII com o texto e o caminho da imagem da carta.
    Substitua por um renderer gráfico ao migrar para Pygame/Tkinter.
    """
    caminho_completo = os.path.join(_RAIZ_PROJETO, carta.imagem)
    existe = os.path.isfile(caminho_completo)
    status = "✅ Encontrada" if existe else "⚠️  Arquivo não encontrado"

    largura = 52
    linha_h = "─" * largura

    print(f"\n  ╔{linha_h}╗")
    print(f"  ║{'CARTA SACADA':^{largura}}║")
    print(f"  ╠{linha_h}╣")

    # Quebra descrição em linhas de até (largura-2) caracteres
    palavras = carta.descricao.split()
    linhas, linha_atual = [], ""
    for palavra in palavras:
        if len(linha_atual) + len(palavra) + 1 <= largura - 2:
            linha_atual += (" " if linha_atual else "") + palavra
        else:
            linhas.append(linha_atual)
            linha_atual = palavra
    if linha_atual:
        linhas.append(linha_atual)

    for linha in linhas:
        print(f"  ║  {linha:<{largura - 2}}║")

    print(f"  ╠{linha_h}╣")
    print(f"  ║  {'🖼  ' + carta.imagem:<{largura - 2}}║")
    print(f"  ║  {status:<{largura - 2}}║")
    print(f"  ╚{linha_h}╝\n")


# ---------------------------------------------------------------------------
# DECK DE SORTE  (cartas 1–8, 19, 20)
# ---------------------------------------------------------------------------

def _criar_cartas_sorte() -> list[Carta]:
    """
    10 cartas de Sorte — efeitos geralmente positivos.
    Imagens: carta_sorte_01…08, carta_sorte_19, carta_sorte_20
    """
    b = "assets/cartas"
    return [
        Carta(                                              # 1
            descricao="Avance até o Início. Receba $200.",
            tipo=TipoEfeito.MOVER_PARA,
            casa_destino=0,
            passa_pelo_inicio=True,
            imagem=f"{b}/carta_sorte_01.png",
        ),
        Carta(                                              # 2
            descricao="Banco paga dividendos. Receba $50.",
            tipo=TipoEfeito.RECEBER_BANCO,
            valor=50,
            imagem=f"{b}/carta_sorte_02.png",
        ),
        Carta(                                              # 3
            descricao="Seu prédio e empréstimo vencem. Receba $150.",
            tipo=TipoEfeito.RECEBER_BANCO,
            valor=150,
            imagem=f"{b}/carta_sorte_03.png",
        ),
        Carta(                                              # 4
            descricao="Presente de aniversário! Receba $10 de cada jogador.",
            tipo=TipoEfeito.RECEBER_JOGADORES,
            valor=10,
            imagem=f"{b}/carta_sorte_04.png",
        ),
        Carta(                                              # 5
            descricao="Você ganhou um concurso de palavras cruzadas. Receba $100.",
            tipo=TipoEfeito.RECEBER_BANCO,
            valor=100,
            imagem=f"{b}/carta_sorte_05.png",
        ),
        Carta(                                              # 6
            descricao="Reembolso de imposto de renda. Receba $20.",
            tipo=TipoEfeito.RECEBER_BANCO,
            valor=20,
            imagem=f"{b}/carta_sorte_06.png",
        ),
        Carta(                                              # 7
            descricao="Saia da prisão gratuitamente. Guarde este cartão.",
            tipo=TipoEfeito.SAIR_PRISAO,
            imagem=f"{b}/carta_sorte_07.png",
        ),
        Carta(                                              # 8
            descricao="Avance até a Avenida São João.",
            tipo=TipoEfeito.MOVER_PARA,
            casa_destino=24,        # ⚠️ Ajustar ao índice real do tabuleiro
            passa_pelo_inicio=True,
            imagem=f"{b}/carta_sorte_08.png",
        ),
        Carta(                                              # 19
            descricao="Receba $25 de serviços prestados.",
            tipo=TipoEfeito.RECEBER_BANCO,
            valor=25,
            imagem=f"{b}/carta_sorte_19.png",
        ),
        Carta(                                              # 20
            descricao="Saia da prisão gratuitamente. Guarde este cartão.",
            tipo=TipoEfeito.SAIR_PRISAO,
            imagem=f"{b}/carta_sorte_20.png",
        ),
    ]


# ---------------------------------------------------------------------------
# DECK DE AZAR  (cartas 9–18)
# ---------------------------------------------------------------------------

def _criar_cartas_azar() -> list[Carta]:
    """
    10 cartas de Azar — efeitos geralmente negativos ou neutros.
    Imagens: carta_azar_09…18
    """
    b = "assets/cartas"
    return [
        Carta(                                              # 9
            descricao="Serviços médicos. Pague $50.",
            tipo=TipoEfeito.PAGAR_BANCO,
            valor=50,
            imagem=f"{b}/carta_azar_09.png",
        ),
        Carta(                                              # 10
            descricao="Multa por excesso de velocidade. Pague $15.",
            tipo=TipoEfeito.PAGAR_BANCO,
            valor=15,
            imagem=f"{b}/carta_azar_10.png",
        ),
        Carta(                                              # 11
            descricao="Vá direto para a prisão. Não passe pelo Início.",
            tipo=TipoEfeito.IR_PARA_PRISAO,
            passa_pelo_inicio=False,
            imagem=f"{b}/carta_azar_11.png",
        ),
        Carta(                                              # 12
            descricao="Reforma geral: pague $25 por andar construído.",
            tipo=TipoEfeito.PAGAR_POR_ANDAR,
            valor=25,
            imagem=f"{b}/carta_azar_12.png",
        ),
        Carta(                                              # 13
            descricao="Consulta médica. Pague $100.",
            tipo=TipoEfeito.PAGAR_BANCO,
            valor=100,
            imagem=f"{b}/carta_azar_13.png",
        ),
        Carta(                                              # 14
            descricao="Você foi multado. Pague $15.",
            tipo=TipoEfeito.PAGAR_BANCO,
            valor=15,
            imagem=f"{b}/carta_azar_14.png",
        ),
        Carta(                                              # 15
            descricao="Pague impostos escolares de $150.",
            tipo=TipoEfeito.PAGAR_BANCO,
            valor=150,
            imagem=f"{b}/carta_azar_15.png",
        ),
        Carta(                                              # 16
            descricao="Você perdeu uma aposta! Pague $10 a cada jogador.",
            tipo=TipoEfeito.PAGAR_JOGADORES,
            valor=10,
            imagem=f"{b}/carta_azar_16.png",
        ),
        Carta(                                              # 17
            descricao="Volte ao Início.",
            tipo=TipoEfeito.MOVER_PARA,
            casa_destino=0,
            passa_pelo_inicio=False,    # Não recebe $200 ao voltar
            imagem=f"{b}/carta_azar_17.png",
        ),
        Carta(                                              # 18
            descricao="Reformas em seus imóveis: $40 por andar.",
            tipo=TipoEfeito.PAGAR_POR_ANDAR,
            valor=40,
            imagem=f"{b}/carta_azar_18.png",
        ),
    ]


# ---------------------------------------------------------------------------
# DECK — BARALHO JOGÁVEL
# ---------------------------------------------------------------------------

class Deck:
    """
    Baralho embaralhado com reposição automática (RF-011/6).

    Quando a pilha acaba, reembaralha tudo automaticamente —
    idêntico ao comportamento do jogo físico.

    Cartas SAIR_PRISAO ficam com o jogador até serem usadas;
    essa lógica é responsabilidade do game.py (chame devolver()
    quando o jogador usar ou perder o cartão).
    """

    def __init__(self, cartas: list[Carta], seed: int = None):
        self._originais = cartas[:]
        self._pilha: list[Carta] = []
        self._descartadas: list[Carta] = []
        self._rng = random.Random(seed)
        self._embaralhar()

    def _embaralhar(self) -> None:
        self._pilha = self._originais[:]
        self._rng.shuffle(self._pilha)
        self._descartadas.clear()

    def sacar(self) -> Carta:
        """Saca a carta do topo; reembaralha automaticamente se vazio."""
        if not self._pilha:
            print("  🔄 Deck vazio — reembaralhando...")
            self._embaralhar()
        carta = self._pilha.pop()
        self._descartadas.append(carta)
        _exibir_imagem_terminal(carta)
        return carta

    def devolver(self, carta: Carta) -> None:
        """
        Devolve uma carta ao pool de descartadas.
        Use quando o jogador consumir um cartão 'Saia da Prisão'.
        """
        if carta not in self._descartadas:
            self._descartadas.append(carta)

    def __len__(self) -> int:
        return len(self._pilha)

    def __repr__(self) -> str:
        return (
            f"Deck({len(self._pilha)} restantes, "
            f"{len(self._descartadas)} descartadas)"
        )


# ---------------------------------------------------------------------------
# CONSTRUTORES PÚBLICOS
# ---------------------------------------------------------------------------

def criar_deck_sorte(seed: int = None) -> Deck:
    """Retorna um Deck de Sorte (cartas 1–8, 19, 20) embaralhado."""
    return Deck(_criar_cartas_sorte(), seed=seed)


def criar_deck_azar(seed: int = None) -> Deck:
    """Retorna um Deck de Azar (cartas 9–18) embaralhado."""
    return Deck(_criar_cartas_azar(), seed=seed)


# ---------------------------------------------------------------------------
# PROCESSADOR DE EFEITOS
# ---------------------------------------------------------------------------

def aplicar_carta(
    carta: Carta,
    jogador_atual,
    todos_jogadores: list,
    tabuleiro,
    transacoes_mod,
) -> dict:
    """
    RF-012/6: Executa o efeito da carta e retorna um dict de resultado
    para que o game.py decida a próxima transição de estado.

    Retorno
    -------
    {
        "moveu"        : bool,
        "nova_posicao" : int | None,
        "passa_inicio" : bool,
        "preso"        : bool,
        "crise"        : bool,
        "cartao_prisao": bool,
    }
    """
    resultado = {
        "moveu":          False,
        "nova_posicao":   None,
        "passa_inicio":   False,
        "preso":          False,
        "crise":          False,
        "cartao_prisao":  False,
    }

    jogadores_ativos = [
        j for j in todos_jogadores
        if j.ativo and j.id != jogador_atual.id
    ]

    # ── RECEBER DO BANCO ────────────────────────────────────────────────────
    if carta.tipo == TipoEfeito.RECEBER_BANCO:
        jogador_atual.receber(carta.valor, motivo=carta.descricao)

    # ── PAGAR AO BANCO ──────────────────────────────────────────────────────
    elif carta.tipo == TipoEfeito.PAGAR_BANCO:
        saldo_ok = jogador_atual.debitar(carta.valor, motivo=carta.descricao)
        resultado["crise"] = not saldo_ok

    # ── RECEBER DE CADA JOGADOR ─────────────────────────────────────────────
    elif carta.tipo == TipoEfeito.RECEBER_JOGADORES:
        for outro in jogadores_ativos:
            outro.debitar(
                carta.valor,
                motivo=f"Pagamento para {jogador_atual.nome} (carta)"
            )
            jogador_atual.receber(
                carta.valor,
                motivo=f"Recebido de {outro.nome} (carta)"
            )

    # ── PAGAR A CADA JOGADOR ────────────────────────────────────────────────
    elif carta.tipo == TipoEfeito.PAGAR_JOGADORES:
        for outro in jogadores_ativos:
            saldo_ok = jogador_atual.debitar(
                carta.valor,
                motivo=f"Pagamento para {outro.nome} (carta)"
            )
            outro.receber(
                carta.valor,
                motivo=f"Recebido de {jogador_atual.nome} (carta)"
            )
            if not saldo_ok:
                resultado["crise"] = True
                break

    # ── IR PARA PRISÃO ──────────────────────────────────────────────────────
    elif carta.tipo == TipoEfeito.IR_PARA_PRISAO:
        jogador_atual.entrar_na_prisao()
        resultado["preso"]        = True
        resultado["moveu"]        = True
        resultado["nova_posicao"] = 10      # Índice da casa Prisão

    # ── MOVER PARA CASA ESPECÍFICA ──────────────────────────────────────────
    elif carta.tipo == TipoEfeito.MOVER_PARA:
        pos_antiga = jogador_atual.posicao
        jogador_atual.posicao = carta.casa_destino
        resultado["moveu"]        = True
        resultado["nova_posicao"] = carta.casa_destino

        passou = carta.passa_pelo_inicio and carta.casa_destino <= pos_antiga
        resultado["passa_inicio"] = passou
        if passou:
            transacoes_mod.processar_inicio(jogador_atual)

    # ── SAIR DA PRISÃO (guardar cartão) ────────────────────────────────────
    elif carta.tipo == TipoEfeito.SAIR_PRISAO:
        jogador_atual.tem_cartao_sair_prisao = True
        resultado["cartao_prisao"] = True
        print(f"  🎫 {jogador_atual.nome} guardou o cartão 'Saia da Prisão'!")

    # ── PAGAR POR ANDAR ─────────────────────────────────────────────────────
    elif carta.tipo == TipoEfeito.PAGAR_POR_ANDAR:
        total_andares = sum(
            tabuleiro.get_casa(pid).andares
            for pid in jogador_atual.propriedades
        )
        total_devido = carta.valor * total_andares
        if total_devido > 0:
            saldo_ok = jogador_atual.debitar(
                total_devido,
                motivo=(
                    f"{carta.descricao} "
                    f"({total_andares} andar(es) × ${carta.valor})"
                )
            )
            resultado["crise"] = not saldo_ok
        else:
            print(
                f"  ℹ️  {jogador_atual.nome} não tem andares construídos. "
                "Sem cobrança."
            )

    return resultado