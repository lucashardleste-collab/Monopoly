# 🎲 Banco Imobiliário / Monopoly Digital

### 🏫 Instituto Federal de Educação, Ciência e Tecnologia de São Paulo (IFSP)
* **Componente Curricular:** Lógica de Programação 
* **Equipe de Desenvolvimento (Stakeholders):** 
  * Arthur Penna
  * [Lucas Lopes](https://github.com/lucashardleste-collab)
  * Pedro Cauã 
  * [Sidney Aragão](https://github.com/Sidney010)
  * [Victor Maia](https://github.com/VictorRai07)
* **Público-Alvo:** Jogos de tabuleiros voltados para todos os públicos, acima de 8 anos (devido aos cálculos matemáticos aplicados)
* **Docentes:** Professores Miyuki e Evandro
---

## 📌 1. Visão Geral do Projeto

Este projeto consiste no desenvolvimento de uma versão digital completa do clássico jogo de tabuleiro **Banco Imobiliário (Monopoly)** utilizando Python. O projeto é focado em simular um ambiente competitivo e baseado em turnos, onde os jogadores precisam gerenciar capital, transacionar ativos imobiliários e mitigar o risco de insolvência.

### 🎯 Foco Pedagógico e de Conscientização Financeira
Mais do que um exercício prático de algoritmo, este software foi concebido como um laboratório prático para o desenvolvimento de competências essenciais:
1. **Incentivo à Matemática Financeira:** Os jogadores exercitam tomadas de decisão baseadas em cálculos de custos, retornos sobre investimentos (ao evoluir propriedades com andares) e negociações com valores customizados.
2. **Controle de Gastos e Orçamento:** O jogo pune severamente comportamentos impulsivos. Manter liquidez (dinheiro em caixa) é vital para sobreviver a cobranças inesperadas de aluguéis ou cartas de azar.
3. **Gerenciamento de Riscos:** Através das mecânicas de hipoteca e falência, os alunos compreendem de maneira prática o impacto do endividamento descontrolado e a importância de uma reserva de contingência.

---

## 🏗️ 2. Arquitetura e Engenharia de Software

Para garantir que o código seja limpo, livre de bugs transacionais e escalável, a equipe adotou três diretrizes arquiteturais estritas:

* **Separação de Conceitos (SoC):** A lógica de negócio (regras, saldos, dados) é totalmente isolada da interface visual. O jogo é capaz de rodar inteiramente via terminal (CLI) antes de ganhar uma interface gráfica.
* **Arquitetura Baseada em Estados (State Pattern):** O fluxo do jogo é controlado por uma máquina de estados rígida (ex: `AguardandoDados` $\rightarrow$ `AvaliandoCasa` $\rightarrow$ `CriseFinanceira` $\rightarrow$ `FimDeTurno`) para evitar condições de corrida ou transações financeiras duplicadas.
* **Composição sobre Herança:** As casas do tabuleiro utilizam comportamentos acopláveis. Em vez de criar uma árvore complexa de herança, uma casa possui um tipo e um conjunto de regras associadas.

---

## 🛠️ 3. Como Executar o Projeto

### Pré-requisitos
* Python 3.10 ou superior instalado no sistema.
* Dependências gráficas instaladas (conforme o framework escolhido pela equipe).
