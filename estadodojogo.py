from abc import ABC, abstractmethod


class EstadoJogo(ABC):
    """Classe base abstrata que atua como barreira de segurança."""

    def __init__(self, jogo):
        self.jogo = jogo  # Referência para o contexto (MonopolyGame)

    def rolar_dados(self):
        print("❌ Não pode rolar os dados nesta fase do turno!")

    def comprar_propriedade(self):
        print("❌ Não pode comprar nada nesta fase!")

    def resolver_crise_hipoteca(self):
        print("❌ Não está em crise financeira!")

    def passar_vez(self):
        print("❌ Não pode passar a vez sem resolver as pendências do turno!")


class EstadoAguardandoDados(EstadoJogo):
    def rolar_dados(self):
        jogador = self.jogo.jogador_atual()
        resultado = self.jogo.dados.rolar()  # RF-005/3
        print(f"🎲 {jogador.nome} rolou os dados e tirou {resultado.total}!")

        # Movimentação circular (RF-006/3)
        nova_pos, passou_inicio = jogador.mover(resultado.total, self.jogo.tabuleiro.total)

        if passou_inicio:  # RF-007/3
            print("💰 Passaste pelo Início! Recebeste o teu salário.")
            jogador.saldo += 200

        # CORREÇÃO: Indentação corrigida para fazer parte do método rolar_dados
        # Transição rígida obrigatória: Avança para a avaliação da casa
        self.jogo.definir_estado(EstadoAvaliandoCasa(self.jogo))
        # Executa automaticamente a avaliação assim que entra no estado
        self.jogo.estado_atual.avaliar_casa_automatico()


class EstadoAvaliandoCasa(EstadoJogo):
    def avaliar_casa_automatico(self):
        """Decide o destino do jogador com base na casa onde aterrou."""
        jogador = self.jogo.jogador_atual()
        casa = self.jogo.tabuleiro.get_casa(jogador.posicao)
        print(f"📍 Paraste na casa: {casa.nome}")

        if casa.tipo == "Propriedade" and casa.dono is None:
            # RF-008/4: Aguarda que o jogador tome a decisão de comprar
            print(f"🏠 {casa.nome} está livre! Podes [Comprar] ou terminar o turno.")
            # O jogo permanece neste estado aguardando ação e bloqueando novos dados

        elif casa.tipo == "Propriedade" and casa.dono != jogador and not casa.hipotecada:
            # RF-009/4: Cobrança automática de aluguer
            aluguer = casa.calcular_aluguel()
            print(f"💸 Esta casa é do {casa.dono.nome}! Aluguer: ${aluguer}")

            if jogador.saldo >= aluguer:
                jogador.saldo -= aluguer
                casa.dono.saldo += aluguer
                print("✅ Aluguer pago com sucesso.")
                self.jogo.definir_estado(EstadoFimDeTurno(self.jogo))
            else:
                # RF-013/7: Se não tem saldo, entra RIGIDAMENTE em Modo de Crise
                print(f"⚠️ Saldo insuficiente! Entraste em CRISE FINANCEIRA.")
                self.jogo.definir_estado(EstadoCriseFinanceira(self.jogo))
        else:
            # Casa sem efeito (Ex: Férias, ou propriedade tua) -> Vai direto para o fim
            self.jogo.definir_estado(EstadoFimDeTurno(self.jogo))

    def comprar_propriedade(self):
        """Ativado apenas se o jogador decidir comprar a propriedade livre."""
        jogador = self.jogo.jogador_atual()
        casa = self.jogo.tabuleiro.get_casa(jogador.posicao)

        if jogador.saldo >= casa.preco:
            jogador.saldo -= casa.preco
            casa.dono = jogador
            print(f"🎉 Compraste {casa.nome} com sucesso!")
            self.jogo.definir_estado(EstadoFimDeTurno(self.jogo))
        else:
            print("❌ Não tens saldo suficiente para comprar esta propriedade!")


class EstadoCriseFinanceira(EstadoJogo):
    def resolver_crise_hipoteca(self):
        """RF-014/7: Menu forçado. O jogador só sai daqui se o saldo for >= 0."""
        jogador = self.jogo.jogador_atual()

        # (Aqui rodará a lógica de escolher propriedade e hipotecar...)
        print("🔧 Propriedade hipotecada. Saldo atualizado.")

        if jogador.saldo >= 0:
            print("✅ Saldo regularizado! A crise foi resolvida.")
            self.jogo.definir_estado(EstadoFimDeTurno(self.jogo))
        else:
            print(f"⚠️ O teu saldo ainda é negativo (${jogador.saldo}). Hipoteca mais bens!")


class EstadoFimDeTurno(EstadoJogo):
    # CORREÇÃO: Nome corrigido para 'passar_vez' (com dois S) para bater com game.py
    def passar_vez(self):
        print("🔄 Turno concluído.")
        self.jogo.avancar_proximo_jogador()
        # O próximo jogador começa obrigatoriamente à espera dos dados
        self.jogo.definir_estado(EstadoAguardandoDados(self.jogo))

# src/core/game.py
from src.core.estado import EstadoAguardandoDados

class MonopolyGame:
    def __init__(self, lista_jogadores, tabuleiro, dados):
        # --- ESTADO PASSIVO (DADOS/MEMÓRIA) ---
        self.jogadores = lista_jogadores  # RF-003/2
        self.tabuleiro = tabuleiro        # RF-001/1
        self.dados = dados                # RF-005/3
        self.turno_atual = 0              # RF-004/2

        # --- ESTADO ATIVO (CONTROLADOR DA MÁQUINA) ---
        # O jogo começa rigidamente no estado de aguardar os dados do primeiro jogador
        self.estado_atual = EstadoAguardandoDados(self)

    def jogador_atual(self):
        return self.jogadores[self.turno_atual]

    def definir_estado(self, novo_estado):
        """Troca o 'porteiro' das regras do jogo em tempo real."""
        print(f"🔄 [MÁQUINA]: Transição para {type(novo_estado).__name__}")
        self.estado_atual = novo_estado

    def avancar_proximo_jogador(self):
        """Avança o ponteiro do turno para o próximo jogador ativo."""
        self.turno_atual = (self.turno_atual + 1) % len(self.jogadores)

    # --- ENTRADAS DE COMANDOS (CLI / EVENTOS DE BOTÕES DA GUI) ---
    def clique_rolar_dados(self):
        self.estado_atual.rolar_dados()

    def clique_comprar(self):
        self.estado_atual.comprar_propriedade()

    def clique_hipotecar(self):
        self.estado_atual.resolver_crise_hipoteca()

    def clique_passar_vez(self):
        self.estado_atual.passar_vez()