# src/core/estado.py
from enum import Enum, auto


class EstadoJogo(Enum):
    """
    Máquina de estados rígida — cada valor é uma fase do turno.

    O fluxo normal de um turno é:
    AGUARDANDO_DADOS
        → MOVENDO
            → AVALIANDO_CASA
                → (COMPRA | ALUGUEL | SORTE_AZAR | CRISE | EFEITO_ESPECIAL)
                    → FIM_DE_TURNO
                        → AGUARDANDO_DADOS  (próximo jogador)

    Fluxos alternativos:
    AGUARDANDO_DADOS → NEGOCIACAO → AGUARDANDO_DADOS (mesma vez)
    AVALIANDO_CASA   → CRISE_FINANCEIRA → (HIPOTECA | FALENCIA)
    """
    # --- Fluxo Principal ---
    AGUARDANDO_DADOS    = auto()   # Jogador pode negociar ou rolar os dados
    MOVENDO             = auto()   # Dados rolados, peão se movendo
    AVALIANDO_CASA      = auto()   # Chegou na casa, qual o efeito?

    # --- Desdobramentos de AVALIANDO_CASA ---
    COMPRA              = auto()   # Casa disponível, jogador decide comprar
    COBRANDO_ALUGUEL    = auto()   # Casa de outro jogador
    SORTE_AZAR          = auto()   # Sacou uma carta
    EFEITO_ESPECIAL     = auto()   # Início, Prisão, Imposto, etc.

    # --- Fluxo de Crise (RF-013/7 a RF-015/7) ---
    CRISE_FINANCEIRA    = auto()   # Saldo negativo após débito
    HIPOTECANDO         = auto()   # Jogador escolhe o que hipotecar
    FALENCIA            = auto()   # Sem saída — remove jogador

    # --- Fluxo de Negociação (RF-016/8 a RF-018/8) ---
    NEGOCIACAO          = auto()   # Proposta aberta entre jogadores

    # --- Controle de Turno ---
    FIM_DE_TURNO        = auto()   # Turno encerrado, passa para o próximo
    FIM_DE_JOGO         = auto()   # Só 1 jogador ativo — game over


class MaquinaDeEstados:
    """
    Controla e valida as transições de estado.

    POR QUE isso importa?
    Sem isso, nada impede de chamar 'cobrar_aluguel()' quando o jogo
    está em estado de NEGOCIACAO. Com a máquina, qualquer transição
    inválida explode com mensagem clara — bem melhor que um bug silencioso
    que só aparece na apresentação. 🙂
    """

    # Mapa de transições válidas: estado_atual → [estados_possíveis]
    _TRANSICOES: dict[EstadoJogo, list[EstadoJogo]] = {
        EstadoJogo.AGUARDANDO_DADOS: [
            EstadoJogo.MOVENDO,
            EstadoJogo.NEGOCIACAO,
            EstadoJogo.FIM_DE_JOGO,
        ],
        EstadoJogo.MOVENDO: [
            EstadoJogo.AVALIANDO_CASA,
        ],
        EstadoJogo.AVALIANDO_CASA: [
            EstadoJogo.COMPRA,
            EstadoJogo.COBRANDO_ALUGUEL,
            EstadoJogo.SORTE_AZAR,
            EstadoJogo.EFEITO_ESPECIAL,
            EstadoJogo.FIM_DE_TURNO,   # Casa sem efeito (ex: Férias de passagem)
            EstadoJogo.AGUARDANDO_DADOS,
        ],
        EstadoJogo.COMPRA: [
            EstadoJogo.FIM_DE_TURNO,
            EstadoJogo.CRISE_FINANCEIRA,
            EstadoJogo.AGUARDANDO_DADOS,   # ← duplo após compra
        ],
        EstadoJogo.COBRANDO_ALUGUEL: [
            EstadoJogo.FIM_DE_TURNO,
            EstadoJogo.CRISE_FINANCEIRA,
            EstadoJogo.AGUARDANDO_DADOS,   # ← duplo após aluguel
        ],
        EstadoJogo.SORTE_AZAR: [
            EstadoJogo.FIM_DE_TURNO,
            EstadoJogo.CRISE_FINANCEIRA,
            EstadoJogo.EFEITO_ESPECIAL,
            EstadoJogo.AGUARDANDO_DADOS,   # ← duplo após carta
        ],
        EstadoJogo.EFEITO_ESPECIAL: [
            EstadoJogo.FIM_DE_TURNO,
            EstadoJogo.CRISE_FINANCEIRA,
            EstadoJogo.AGUARDANDO_DADOS,   # ← duplo após efeito
        ],
        EstadoJogo.CRISE_FINANCEIRA: [
            EstadoJogo.HIPOTECANDO,
            EstadoJogo.FALENCIA,
        ],
        EstadoJogo.HIPOTECANDO: [
            EstadoJogo.FIM_DE_TURNO,   # Conseguiu se recuperar
            EstadoJogo.FALENCIA,       # Hipotecou tudo e ainda negativo
        ],
        EstadoJogo.FALENCIA: [
            EstadoJogo.FIM_DE_TURNO,
            EstadoJogo.FIM_DE_JOGO,
        ],
        EstadoJogo.NEGOCIACAO: [
            EstadoJogo.AGUARDANDO_DADOS, # Proposta aceita/recusada, volta ao turno
            EstadoJogo.CRISE_FINANCEIRA, # Aceitou proposta e ficou sem grana
        ],
        EstadoJogo.FIM_DE_TURNO: [
            EstadoJogo.AGUARDANDO_DADOS, # Próximo jogador
            EstadoJogo.FIM_DE_JOGO,
        ],
        EstadoJogo.FIM_DE_JOGO: [],      # Estado terminal
    }

    def __init__(self):
        self.estado_atual = EstadoJogo.AGUARDANDO_DADOS
        self.historico: list[EstadoJogo] = [self.estado_atual]

    def transicionar(self, novo_estado: EstadoJogo) -> None:
        """
        Tenta mudar de estado. Explode se a transição for inválida.
        Melhor quebrar aqui com mensagem clara do que ter comportamento
        indefinido lá na frente.
        """
        permitidos = self._TRANSICOES.get(self.estado_atual, [])
        if novo_estado not in permitidos:
            raise ValueError(
                f"Transição inválida: {self.estado_atual.name} "
                f"→ {novo_estado.name}\n"
                f"Permitidos: {[e.name for e in permitidos]}"
            )
        self.historico.append(novo_estado)
        self.estado_atual = novo_estado

    def em(self, estado: EstadoJogo) -> bool:
        """Atalho legível para checar estado atual."""
        return self.estado_atual == estado

    def __repr__(self) -> str:
        return f"Estado: {self.estado_atual.name}"