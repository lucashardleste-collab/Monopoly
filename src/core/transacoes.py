# src/core/transacoes.py
from src.core.jogador import Jogador
from src.core.propriedade import Propriedade, CorGrupo
from src.core.tabuleiro import Tabuleiro


# ---------------------------------------------------------------------------
# CONSTANTES DO JOGO
# ---------------------------------------------------------------------------
SALARIO_INICIO = 200          # Bônus ao passar pelo Início (RF-007/3)
MULTA_PRISAO   = 50           # Valor para sair da prisão na 3ª tentativa
BONUS_INICIO   = 200          # Alias semântico — evita magic numbers


# ---------------------------------------------------------------------------
# SEÇÃO 1 — PASSAGEM PELO INÍCIO
# ---------------------------------------------------------------------------

def processar_inicio(jogador: Jogador) -> None:
    """
    RF-007/3: Paga salário ao jogador que passou pela casa Início.
    Separado em função própria — é chamado pelo game.py após mover.
    """
    jogador.receber(SALARIO_INICIO, motivo="Passou pelo Início")


# ---------------------------------------------------------------------------
# SEÇÃO 2 — COMPRA DE PROPRIEDADE
# ---------------------------------------------------------------------------

def comprar_propriedade(jogador: Jogador, propriedade: Propriedade) -> bool:
    """
    RF-008/4: Jogador tenta comprar uma propriedade disponível.
    Retorna True se compra realizada, False se saldo insuficiente.

    Não lança exceção em saldo insuficiente — é uma decisão de negócio,
    não um erro. O game.py decide o que fazer com o False.
    """
    if not propriedade.esta_disponivel():
        print(f"  ⚠️  {propriedade.nome} não está disponível para compra.")
        return False

    if not jogador.pode_comprar(propriedade.preco):
        print(f"  ⚠️  {jogador.nome} não tem saldo suficiente. "
              f"(Saldo: ${jogador.saldo} | Preço: ${propriedade.preco})")
        return False

    jogador.debitar(propriedade.preco, motivo=f"Compra de {propriedade.nome}")
    propriedade.dono_id = jogador.id
    jogador.adicionar_propriedade(propriedade.id)

    print(f"  🏠 {jogador.nome} comprou {propriedade.nome} por ${propriedade.preco}!")
    return True


# ---------------------------------------------------------------------------
# SEÇÃO 3 — COBRANÇA DE ALUGUEL
# ---------------------------------------------------------------------------

def cobrar_aluguel(
    inquilino: Jogador,
    dono: Jogador,
    propriedade: Propriedade
) -> bool:
    """
    RF-009/4: Deduz aluguel do inquilino e soma ao dono.
    Retorna True se saldo OK, False se inquilino entrou em crise.

    DECISÃO: o dono recebe mesmo que o inquilino fique negativo.
    Regra oficial do Monopoly — a crise é problema do inquilino.
    O retorno False sinaliza para game.py disparar CRISE_FINANCEIRA.
    """
    # Dono não paga aluguel pra si mesmo
    if inquilino.id == dono.id:
        return True

    aluguel = propriedade.calcular_aluguel()

    if aluguel == 0:
        print(f"  ℹ️  {propriedade.nome} está hipotecada. Sem cobrança.")
        return True

    print(f"  🏦 Aluguel de {propriedade.nome}: ${aluguel}")
    saldo_ok = inquilino.debitar(aluguel, motivo=f"Aluguel em {propriedade.nome}")
    dono.receber(aluguel, motivo=f"Aluguel recebido de {inquilino.nome}")

    return saldo_ok


# ---------------------------------------------------------------------------
# SEÇÃO 4 — CONSTRUÇÃO DE ANDARES
# ---------------------------------------------------------------------------

def verificar_monopolio(
    jogador: Jogador,
    cor: CorGrupo,
    tabuleiro: Tabuleiro
) -> bool:
    """
    RF-009/5: Checa se jogador possui TODAS as propriedades de uma cor.
    Propriedades hipotecadas ainda contam para o monopólio.
    """
    propriedades_da_cor = tabuleiro.get_propriedades_da_cor(cor)

    if not propriedades_da_cor:
        return False

    return all(p.dono_id == jogador.id for p in propriedades_da_cor)


def construir_andar(
    jogador: Jogador,
    propriedade: Propriedade,
    tabuleiro: Tabuleiro
) -> bool:
    """
    RF-010/5: Constrói um andar na propriedade se monopólio verificado.
    Máximo de 4 andares (índice 0-3 em aluguel_por_andar).

    REGRA: construção uniforme — diferença máxima de 1 andar
    entre propriedades do mesmo grupo. Implementação simplificada
    aqui; validação completa pode ser adicionada depois (YAGNI).
    """
    if propriedade.dono_id != jogador.id:
        print(f"  ⚠️  {jogador.nome} não é dono de {propriedade.nome}.")
        return False

    if propriedade.cor is None:
        print(f"  ⚠️  {propriedade.nome} não aceita construção.")
        return False

    if not verificar_monopolio(jogador, propriedade.cor, tabuleiro):
        print(f"  ⚠️  {jogador.nome} não tem monopólio da cor {propriedade.cor.value}.")
        return False

    MAX_ANDARES = 4
    if propriedade.andares >= MAX_ANDARES:
        print(f"  ⚠️  {propriedade.nome} já está no máximo de andares.")
        return False

    if not jogador.pode_comprar(propriedade.preco_andar):
        print(f"  ⚠️  Saldo insuficiente para construir. "
              f"(Saldo: ${jogador.saldo} | Custo: ${propriedade.preco_andar})")
        return False

    jogador.debitar(propriedade.preco_andar,
                    motivo=f"Construção em {propriedade.nome}")
    propriedade.andares += 1

    print(f"  🏗️  {jogador.nome} construiu andar {propriedade.andares} "
          f"em {propriedade.nome}! Novo aluguel: ${propriedade.calcular_aluguel()}")
    return True


# ---------------------------------------------------------------------------
# SEÇÃO 5 — HIPOTECA
# ---------------------------------------------------------------------------

def hipotecar_propriedade(jogador: Jogador, propriedade: Propriedade) -> bool:
    """
    RF-014/7: Jogador hipoteca propriedade para levantar capital.
    Propriedade hipotecada não cobra aluguel até ser resgatada.
    """
    if propriedade.dono_id != jogador.id:
        print(f"  ⚠️  {jogador.nome} não é dono de {propriedade.nome}.")
        return False

    if propriedade.hipotecada:
        print(f"  ⚠️  {propriedade.nome} já está hipotecada.")
        return False

    if propriedade.andares > 0:
        print(f"  ⚠️  Venda os andares antes de hipotecar {propriedade.nome}.")
        return False

    propriedade.hipotecada = True
    jogador.receber(propriedade.valor_hipoteca,
                    motivo=f"Hipoteca de {propriedade.nome}")

    print(f"  🏦 {propriedade.nome} hipotecada. "
          f"{jogador.nome} recebeu ${propriedade.valor_hipoteca}.")
    return True


def resgatar_hipoteca(jogador: Jogador, propriedade: Propriedade) -> bool:
    """
    Resgata propriedade hipotecada.
    Custo = valor_hipoteca + 10% de juros (regra oficial).
    """
    if not propriedade.hipotecada:
        print(f"  ⚠️  {propriedade.nome} não está hipotecada.")
        return False

    custo_resgate = int(propriedade.valor_hipoteca * 1.1)

    if not jogador.pode_comprar(custo_resgate):
        print(f"  ⚠️  Saldo insuficiente para resgatar. "
              f"(Saldo: ${jogador.saldo} | Custo: ${custo_resgate})")
        return False

    jogador.debitar(custo_resgate, motivo=f"Resgate de hipoteca: {propriedade.nome}")
    propriedade.hipotecada = False

    print(f"  ✅ {propriedade.nome} resgatada por ${custo_resgate}.")
    return True


# ---------------------------------------------------------------------------
# SEÇÃO 6 — FALÊNCIA
# ---------------------------------------------------------------------------

def processar_falencia(
    falido: Jogador,
    credor: Jogador | None,
    tabuleiro: Tabuleiro
) -> None:
    """
    RF-015/7: Remove jogador e redistribui seus bens.

    credor = jogador que recebe as propriedades (quem cobrou o aluguel)
    credor = None significa que as propriedades voltam ao banco (disponíveis).

    FLUXO:
    1. Transfere dinheiro restante ao credor (se houver)
    2. Transfere propriedades ao credor OU devolve ao banco
    3. Remove andares das propriedades devolvidas ao banco
    4. Marca jogador como inativo
    """
    print(f"\n  💀 Iniciando processo de falência de {falido.nome}...")

    # Passo 1: dinheiro restante vai para o credor
    if credor and falido.saldo > 0:
        credor.receber(falido.saldo,
                       motivo=f"Herança da falência de {falido.nome}")

    # Passo 2 e 3: propriedades
    for prop_id in falido.propriedades[:]:           # cópia da lista para iterar
        propriedade = tabuleiro.get_casa(prop_id)

        if credor:
            # Transfere direto para o credor — mantém andares
            propriedade.dono_id = credor.id
            credor.adicionar_propriedade(prop_id)
            print(f"  🔄 {propriedade.nome} transferida para {credor.nome}.")
        else:
            # Volta ao banco — zera tudo
            propriedade.dono_id = None
            propriedade.hipotecada = False
            propriedade.andares = 0
            print(f"  🏦 {propriedade.nome} devolvida ao banco.")

        falido.remover_propriedade(prop_id)

    falido.declarar_falencia()


# ---------------------------------------------------------------------------
# SEÇÃO 7 — PROPOSTAS (TROCAS)
# ---------------------------------------------------------------------------

def processar_proposta(
    proponente: Jogador,
    alvo: Jogador,
    propriedade: Propriedade,
    valor_oferecido: int
) -> bool:
    """
    RF-016/8 a RF-018/8: Processa uma proposta de compra entre jogadores.
    Retorna True se transação realizada.

    DECISÃO: essa função só processa — quem decide aceitar/recusar
    é o game.py (que lida com input do usuário). SRP.
    """
    if propriedade.dono_id != alvo.id:
        print(f"  ⚠️  {alvo.nome} não é dono de {propriedade.nome}.")
        return False

    if not proponente.pode_comprar(valor_oferecido):
        print(f"  ⚠️  {proponente.nome} não tem saldo para essa proposta.")
        return False

    # Transferência financeira
    proponente.debitar(valor_oferecido,
                       motivo=f"Proposta por {propriedade.nome}")
    alvo.receber(valor_oferecido,
                 motivo=f"Venda de {propriedade.nome}")

    # Transferência de propriedade
    propriedade.dono_id = proponente.id
    alvo.remover_propriedade(propriedade.id)
    proponente.adicionar_propriedade(propriedade.id)

    print(f"  🤝 {propriedade.nome} transferida de "
          f"{alvo.nome} para {proponente.nome} por ${valor_oferecido}!")
    return True


# ---------------------------------------------------------------------------
# SEÇÃO 8 — PRISÃO
# ---------------------------------------------------------------------------

def pagar_multa_prisao(jogador: Jogador) -> bool:
    """
    Jogador paga multa para sair da prisão na 3ª tentativa.
    Retorna False se entrar em crise após o pagamento.
    """
    return jogador.debitar(MULTA_PRISAO, motivo="Multa para sair da prisão")  