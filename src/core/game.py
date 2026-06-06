# src/core/game.py
from src.core.jogador import Jogador
from src.core.tabuleiro import Tabuleiro
from src.core.dados import Dados
from src.core.estado import MaquinaDeEstados, EstadoJogo
from src.core.propriedade import TipoCasa
from src.core.cartas import Deck, aplicar_carta
import src.core.transacoes as transacoes
import src.core.cartas as cartas_mod


# ---------------------------------------------------------------------------
# CONSTANTES
# ---------------------------------------------------------------------------

SALDO_INICIAL   = 1500
MAX_DUPLOS      = 3


# ---------------------------------------------------------------------------
# CLASSE PRINCIPAL
# ---------------------------------------------------------------------------

class Monopoly:
    """
    Orquestrador central do jogo.

    RESPONSABILIDADE ÚNICA: coordenar os módulos.
    Não contém regras de negócio — essas vivem em transacoes.py.
    Não contém rendering — esse virá em src/view/ (fase 2).
    """

    def __init__(self, nomes_jogadores: list[str], seed: int = None):
        if len(nomes_jogadores) < 2:
            raise ValueError("Monopoly precisa de pelo menos 2 jogadores.")
        if len(nomes_jogadores) > 6:
            raise ValueError("Monopoly suporta no máximo 6 jogadores.")

        self.tabuleiro    = Tabuleiro()
        self.dados        = Dados(seed=seed)
        self.estado       = MaquinaDeEstados()
        self.deck_sorte   = Deck(cartas_mod._criar_cartas_sorte(), seed=seed)
        self.deck_azar    = Deck(cartas_mod._criar_cartas_azar(), seed=seed)

        self.jogadores: list[Jogador] = [
            Jogador(id=i, nome=nome, saldo=SALDO_INICIAL)
            for i, nome in enumerate(nomes_jogadores)
        ]

        self.indice_atual: int = 0       # Índice do jogador da vez
        self.rodada: int = 1

    # -----------------------------------------------------------------------
    # PROPRIEDADES DE CONVENIÊNCIA
    # -----------------------------------------------------------------------

    @property
    def jogador_atual(self) -> Jogador:
        return self.jogadores[self.indice_atual]

    @property
    def jogadores_ativos(self) -> list[Jogador]:
        return [j for j in self.jogadores if j.ativo]

    def _vencedor(self) -> Jogador | None:
        ativos = self.jogadores_ativos
        return ativos[0] if len(ativos) == 1 else None

    # -----------------------------------------------------------------------
    # LOOP PRINCIPAL
    # -----------------------------------------------------------------------

    def iniciar(self) -> None:
        """
        RF-004/2: Game Loop principal.
        Roda até restar apenas 1 jogador ativo.
        """
        self._cabecalho()

        while not self.estado.em(EstadoJogo.FIM_DE_JOGO):
            jogador = self.jogador_atual

            if not jogador.ativo:
                self._avancar_turno()
                continue

            self._iniciar_turno(jogador)

        self._tela_fim_de_jogo()

    # -----------------------------------------------------------------------
    # TURNO
    # -----------------------------------------------------------------------

    def _iniciar_turno(self, jogador: Jogador) -> None:
        print(f"\n{'═' * 55}")
        print(f"  🎲 Rodada {self.rodada} | Vez de: {jogador.nome}")
        print(f"  📍 Posição: {self.tabuleiro.get_casa(jogador.posicao).nome}"
              f" (casa {jogador.posicao})")
        print(f"  💰 Saldo: ${jogador.saldo}")
        print(f"{'═' * 55}")

        # Fase de negociação (antes dos dados)
        self._fase_negociacao(jogador)

        # Se ainda for a vez dele (não desistiu/faliu na negociação)
        if jogador.ativo and self.estado.em(EstadoJogo.AGUARDANDO_DADOS):
            self._fase_dados(jogador)

        if jogador.ativo and self.estado.em(EstadoJogo.AGUARDANDO_DADOS):
            self._fase_construcao(jogador)

    def _fase_construcao(self, jogador: Jogador) -> None:
        """
        RF-010/5: Permite construir andares antes de rolar os dados.
        Só exibe o menu se o jogador tiver ao menos um monopólio.
        """
        # Descobre quais cores o jogador tem monopólio
        from src.core.propriedade import CorGrupo

        cores_com_monopolio = [
            cor for cor in CorGrupo
            if transacoes.verificar_monopolio(jogador, cor, self.tabuleiro)
        ]

        if not cores_com_monopolio:
            return      # Sem monopólio, sem construção — nem mostra o menu

        # Monta lista de propriedades construíveis
        props_construiveis = [
            self.tabuleiro.get_casa(pid)
            for pid in jogador.propriedades
            if self.tabuleiro.get_casa(pid).cor in cores_com_monopolio
            and self.tabuleiro.get_casa(pid).andares < 4
            and not self.tabuleiro.get_casa(pid).hipotecada
        ]

        if not props_construiveis:
            return      # Todas no máximo de andares

        # Menu em loop — jogador pode construir várias vezes
        while True:
            print(f"\n  🏗️  Você tem monopólio! Deseja construir andares?")
            print(f"  [C] Construir   [ENTER] Pular")
            opcao = input("  › ").strip().upper()

            if opcao != "C":
                break

            # Lista propriedades disponíveis para construção
            props_construiveis = [
                self.tabuleiro.get_casa(pid)
                for pid in jogador.propriedades
                if self.tabuleiro.get_casa(pid).cor in cores_com_monopolio
                and self.tabuleiro.get_casa(pid).andares < 4
                and not self.tabuleiro.get_casa(pid).hipotecada
            ]

            if not props_construiveis:
                print("  ⚠️  Todas as propriedades já estão no máximo.")
                break

            print(f"\n  Propriedades disponíveis (Saldo: ${jogador.saldo}):")
            for i, p in enumerate(props_construiveis):
                proximo_aluguel = (
                    p.aluguel_por_andar[p.andares]
                    if p.andares < len(p.aluguel_por_andar)
                    else "(máx)"
                )

            print(f"  [{i}] {p.nome} | "
                f"Andares: {p.andares}/{len(p.aluguel_por_andar)} | "
                f"Custo: ${p.preco_andar} | "
                f"Aluguel atual: ${p.calcular_aluguel()} → "
                f"${proximo_aluguel}")

            try:
                escolha = int(input("  Escolha o índice › "))
                if 0 <= escolha < len(props_construiveis):
                    transacoes.construir_andar(
                        jogador,
                        props_construiveis[escolha],
                        self.tabuleiro
                    )
                else:
                    print("  ⚠️  Índice inválido.")
            except ValueError:
                print("  ⚠️  Digite um número válido.")

    def _fase_negociacao(self, jogador: Jogador) -> None:
        """RF-016/8: Menu de negociação antes de rolar os dados."""
        if not jogador.propriedades:
            return                   # Sem propriedades, sem negociação

        print("\n  [N] Propor negociação   [ENTER] Rolar os dados")
        opcao = input("  › ").strip().upper()

        if opcao == "N":
            self.estado.transicionar(EstadoJogo.NEGOCIACAO)
            self._fluxo_negociacao(jogador)

    def _fase_dados(self, jogador: Jogador) -> None:
        input(f"\n  {jogador.nome}, pressione ENTER para rolar os dados...")

        # Rola os dados PRIMEIRO — resultado existe para todos os caminhos
        resultado = self.dados.rolar()

        # Regra dos 3 duplos consecutivos — checa APÓS rolar
        if self.dados.tres_duplos_consecutivos():
            print(f"  🚔 3 duplos seguidos! {jogador.nome} vai para a prisão!")
            jogador.entrar_na_prisao()
            self.dados.resetar_duplos()
            self.estado.transicionar(EstadoJogo.MOVENDO)
            self.estado.transicionar(EstadoJogo.AVALIANDO_CASA)
            self._finalizar_turno(jogador)
            return

        # Jogador preso — tenta sair com o resultado já rolado
        if jogador.preso:
            self.estado.transicionar(EstadoJogo.MOVENDO)
            self._turno_preso(jogador, resultado)
            return

        # Movimentação normal
        self.estado.transicionar(EstadoJogo.MOVENDO)
        nova_pos, passou_inicio = jogador.mover(resultado.total, self.tabuleiro.total)

        if passou_inicio:
            transacoes.processar_inicio(jogador)

        casa = self.tabuleiro.get_casa(nova_pos)
        print(f"\n  📍 {jogador.nome} avançou {resultado.total} casas → {casa.nome}")

        self.estado.transicionar(EstadoJogo.AVALIANDO_CASA)
        self._avaliar_casa(jogador, casa)

        # Duplo = joga de novo (se não foi preso)
        if resultado.eh_duplo and not jogador.preso and jogador.ativo:
            print(f"\n  🎯 Duplo! {jogador.nome} joga novamente!")
            self.estado.transicionar(EstadoJogo.AGUARDANDO_DADOS)
            self._fase_dados(jogador)
            return

        self._finalizar_turno(jogador)
    def _turno_preso(self, jogador: Jogador, resultado) -> None:
        print(f"\n  🔒 {jogador.nome} está preso (tentativa {jogador.turnos_preso + 1}/3).")

        # Opção de usar cartão
        if jogador.tem_cartao_sair_prisao:
            print("  [C] Usar cartão 'Saia da Prisão'   [ENTER] Tentar duplo")
            if input("  › ").strip().upper() == "C":
                jogador.tem_cartao_sair_prisao = False
                jogador.preso = False
                jogador.turnos_preso = 0
                print(f"  🎫 {jogador.nome} usou o cartão e saiu da prisão!")
                # Reseta estado e joga normalmente
                self.estado.transicionar(EstadoJogo.AVALIANDO_CASA)
                self.estado.transicionar(EstadoJogo.AGUARDANDO_DADOS)
                self._fase_dados(jogador)
                return

        saiu = jogador.tentar_sair_prisao(resultado.eh_duplo)

        if saiu:
            if jogador.turnos_preso == 0 and not resultado.eh_duplo:
                # 3ª tentativa — paga multa
                saldo_ok = transacoes.pagar_multa_prisao(jogador)
                if not saldo_ok:
                    self.estado.transicionar(EstadoJogo.AVALIANDO_CASA)
                    self._fluxo_crise(jogador, credor=None)
                    return
            print(f"  ✅ {jogador.nome} saiu da prisão!")
            nova_pos, passou_inicio = jogador.mover(resultado.total, self.tabuleiro.total)
            if passou_inicio:
                transacoes.processar_inicio(jogador)
            casa = self.tabuleiro.get_casa(nova_pos)
            print(f"\n  📍 {jogador.nome} avançou {resultado.total} casas → {casa.nome}")
            self.estado.transicionar(EstadoJogo.AVALIANDO_CASA)
            self._avaliar_casa(jogador, casa)
        else:
            print(f"  ❌ {jogador.nome} não tirou duplo. Continua preso.")
            self.estado.transicionar(EstadoJogo.AVALIANDO_CASA)  # ← sem MOVENDO antes

        self._finalizar_turno(jogador)

    # -----------------------------------------------------------------------
    # AVALIAÇÃO DE CASA
    # -----------------------------------------------------------------------

    def _avaliar_casa(self, jogador: Jogador, casa) -> None:
        """
        Despacha para o handler correto baseado no tipo da casa.
        Uma casa = um comportamento. Sem if-elif quilométrico espalhado.
        """
        handlers = {
            TipoCasa.PROPRIEDADE:      self._handler_propriedade,
            TipoCasa.SORTE:            self._handler_sorte,
            TipoCasa.AZAR:             self._handler_azar,
            TipoCasa.IR_PARA_PRISAO:   self._handler_ir_prisao,
            TipoCasa.IMPOSTO:          self._handler_imposto,
            TipoCasa.INICIO:           lambda j, c: None,   # Já tratado no mover
            TipoCasa.FERIAS:           self._handler_ferias,
            TipoCasa.PRISAO:           lambda j, c: None,   # Só visita
        }

        handler = handlers.get(casa.tipo)
        if handler:
            handler(jogador, casa)

    def _handler_propriedade(self, jogador: Jogador, casa) -> None:
        if casa.esta_disponivel():
            self.estado.transicionar(EstadoJogo.COMPRA)
            self._fluxo_compra(jogador, casa)

        elif casa.dono_id != jogador.id:
            self.estado.transicionar(EstadoJogo.COBRANDO_ALUGUEL)
            dono = self._get_jogador_por_id(casa.dono_id)
            saldo_ok = transacoes.cobrar_aluguel(jogador, dono, casa)
            if not saldo_ok:
                self._fluxo_crise(jogador, credor=dono)
        else:
            print(f"  🏠 {jogador.nome} caiu na própria propriedade.")

    def _handler_sorte(self, jogador: Jogador, casa) -> None:
        self.estado.transicionar(EstadoJogo.SORTE_AZAR)
        print(f"\n  🍀 Carta de SORTE:")
        carta = self.deck_sorte.sacar()
        resultado = aplicar_carta(
            carta, jogador, self.jogadores,
            self.tabuleiro, transacoes
        )
        self._processar_resultado_carta(jogador, resultado)

    def _handler_azar(self, jogador: Jogador, casa) -> None:
        self.estado.transicionar(EstadoJogo.SORTE_AZAR)
        print(f"\n  💀 Carta de AZAR:")
        carta = self.deck_azar.sacar()
        resultado = aplicar_carta(
            carta, jogador, self.jogadores,
            self.tabuleiro, transacoes
        )
        self._processar_resultado_carta(jogador, resultado)

    def _handler_ir_prisao(self, jogador: Jogador, casa) -> None:
        self.estado.transicionar(EstadoJogo.EFEITO_ESPECIAL)
        jogador.entrar_na_prisao()

    def _handler_imposto(self, jogador: Jogador, casa) -> None:
        self.estado.transicionar(EstadoJogo.EFEITO_ESPECIAL)
        valor = 200
        print(f"  🧾 Imposto! {jogador.nome} paga ${valor} ao banco.")
        saldo_ok = jogador.debitar(valor, motivo="Imposto")
        if not saldo_ok:
            self._fluxo_crise(jogador, credor=None)

    def _handler_ferias(self, jogador: Jogador, casa) -> None:
        self.estado.transicionar(EstadoJogo.EFEITO_ESPECIAL)
        print(f"  🏖️  {jogador.nome} está de férias. Descanse!")

    def _processar_resultado_carta(self, jogador: Jogador, resultado: dict) -> None:
        if resultado["preso"]:
            self.estado.transicionar(EstadoJogo.EFEITO_ESPECIAL)
        elif resultado["crise"]:
            self._fluxo_crise(jogador, credor=None)

    # -----------------------------------------------------------------------
    # FLUXOS ESPECIAIS
    # -----------------------------------------------------------------------

    def _fluxo_compra(self, jogador: Jogador, propriedade) -> None:
        """RF-008/4: Fluxo de decisão de compra."""
        print(f"\n  🏠 {propriedade.nome} está disponível!")
        print(f"  Preço: ${propriedade.preco} | Seu saldo: ${jogador.saldo}")
        print(f"  [C] Comprar   [ENTER] Passar")
        opcao = input("  › ").strip().upper()

        if opcao == "C":
            transacoes.comprar_propriedade(jogador, propriedade)

    def _fluxo_crise(self, jogador: Jogador, credor: Jogador | None) -> None:
        """
        RF-013/7 a RF-015/7: Modo de crise financeira.
        Loop até saldo positivo ou falência declarada.
        """
        self.estado.transicionar(EstadoJogo.CRISE_FINANCEIRA)
        print(f"\n  🚨 CRISE FINANCEIRA! {jogador.nome} está com saldo ${jogador.saldo}")

        # Filtra propriedades não hipotecadas
        props_disponiveis = [
            self.tabuleiro.get_casa(pid)
            for pid in jogador.propriedades
            if not self.tabuleiro.get_casa(pid).hipotecada
        ]

        if not props_disponiveis:
            self.estado.transicionar(EstadoJogo.FALENCIA)
            transacoes.processar_falencia(jogador, credor, self.tabuleiro)
            self._verificar_fim_de_jogo()
            return

        self.estado.transicionar(EstadoJogo.HIPOTECANDO)

        while jogador.saldo < 0 and jogador.ativo:
            props_disponiveis = [
                self.tabuleiro.get_casa(pid)
                for pid in jogador.propriedades
                if not self.tabuleiro.get_casa(pid).hipotecada
            ]

            if not props_disponiveis:
                # Hipotecou tudo e ainda negativo — falência
                self.estado.transicionar(EstadoJogo.FALENCIA)
                transacoes.processar_falencia(jogador, credor, self.tabuleiro)
                self._verificar_fim_de_jogo()
                return

            print(f"\n  Saldo atual: ${jogador.saldo}")
            print("  Propriedades para hipotecar:")
            for i, p in enumerate(props_disponiveis):
                print(f"  [{i}] {p.nome} — recebe ${p.valor_hipoteca}")

            try:
                escolha = int(input("  Escolha o índice para hipotecar › "))
                if 0 <= escolha < len(props_disponiveis):
                    transacoes.hipotecar_propriedade(jogador, props_disponiveis[escolha])
                else:
                    print("  ⚠️  Índice inválido.")
            except ValueError:
                print("  ⚠️  Digite um número válido.")

    def _fluxo_negociacao(self, jogador: Jogador) -> None:
        """RF-017/8 + RF-018/8: Fluxo completo de proposta entre jogadores."""
        alvos = [j for j in self.jogadores_ativos if j.id != jogador.id and j.propriedades]

        if not alvos:
            print("  ⚠️  Nenhum jogador com propriedades disponível para negociar.")
            self.estado.transicionar(EstadoJogo.AGUARDANDO_DADOS)
            return

        print("\n  Jogadores disponíveis:")
        for i, j in enumerate(alvos):
            print(f"  [{i}] {j.nome}")

        try:
            idx_alvo = int(input("  Escolha o jogador › "))
            alvo = alvos[idx_alvo]

            props_alvo = [self.tabuleiro.get_casa(pid) for pid in alvo.propriedades]
            print(f"\n  Propriedades de {alvo.nome}:")
            for i, p in enumerate(props_alvo):
                print(f"  [{i}] {p.nome} | Preço original: ${p.preco}")

            idx_prop = int(input("  Escolha a propriedade › "))
            propriedade = props_alvo[idx_prop]

            valor = int(input(f"  Quanto oferece por {propriedade.nome}? $"))

            # Pausa — alvo decide
            print(f"\n  ⏸️  {alvo.nome}, você recebeu uma proposta!")
            print(f"  {jogador.nome} quer {propriedade.nome} por ${valor}")
            print(f"  [S] Aceitar   [N] Recusar")
            resposta = input("  › ").strip().upper()

            if resposta == "S":
                saldo_ok = transacoes.processar_proposta(
                    jogador, alvo, propriedade, valor
                )
                if not saldo_ok:
                    self._fluxo_crise(jogador, credor=None)
                    return
            else:
                print(f"  ❌ {alvo.nome} recusou a proposta.")

        except (ValueError, IndexError):
            print("  ⚠️  Entrada inválida. Negociação cancelada.")

        self.estado.transicionar(EstadoJogo.AGUARDANDO_DADOS)

    # -----------------------------------------------------------------------
    # FIM DE TURNO E JOGO
    # -----------------------------------------------------------------------

    def _finalizar_turno(self, jogador: Jogador) -> None:
        """Reseta estado e passa para o próximo jogador."""
        if not self.estado.em(EstadoJogo.FIM_DE_JOGO):
            self.estado.transicionar(EstadoJogo.FIM_DE_TURNO)
            self.dados.resetar_duplos()
            self._verificar_fim_de_jogo()

            if not self.estado.em(EstadoJogo.FIM_DE_JOGO):
                self._avancar_turno()
                self.estado.transicionar(EstadoJogo.AGUARDANDO_DADOS)

    def _avancar_turno(self) -> None:
        self.indice_atual = (self.indice_atual + 1) % len(self.jogadores)
        if self.indice_atual == 0:
            self.rodada += 1

    def _verificar_fim_de_jogo(self) -> None:
        if len(self.jogadores_ativos) <= 1:
            self.estado.transicionar(EstadoJogo.FIM_DE_JOGO)

    # -----------------------------------------------------------------------
    # HELPERS
    # -----------------------------------------------------------------------

    def _get_jogador_por_id(self, jogador_id: int) -> Jogador:
        for j in self.jogadores:
            if j.id == jogador_id:
                return j
        raise ValueError(f"Jogador ID {jogador_id} não encontrado.")

    def _cabecalho(self) -> None:
        print("\n" + "═" * 55)
        print("   🏦  BANCO IMOBILIÁRIO — Python Edition")
        print("═" * 55)
        print("  Jogadores:")
        for j in self.jogadores:
            print(f"   • {j.nome} — Saldo inicial: ${j.saldo}")
        print("═" * 55 + "\n")

    def _tela_fim_de_jogo(self) -> None:
        vencedor = self._vencedor()
        print("\n" + "═" * 55)
        print("  🏆  FIM DE JOGO!")
        if vencedor:
            print(f"  Vencedor: {vencedor.nome} com ${vencedor.saldo}")
        print("═" * 55)