# Sistemas Distribuídos: Ordenação Lógica e Causalidade

Este repositório contém duas simulações práticas desenvolvidas em Python para demonstrar conceitos fundamentais de sincronização e ordenação em Sistemas Distribuídos: **Relógios Lógicos de Lamport** e **Relógios Vetoriais (Vector Clocks)**.

O objetivo do projeto é demonstrar como sistemas descentralizados lidam com o tempo relativo, ordenação de eventos e análise de causalidade em cenários com latência de rede imprevisível.

---

## 📁 Estrutura do Projeto

O projeto é dividido em dois scripts principais:

### 1. Sistema de Chat com Ordenação Total (Relógios de Lamport)
**Arquivo:** `chat_lamport.py`

Uma simulação assíncrona de um chat em grupo onde múltiplos processos (usuários) se comunicam via broadcast. O sistema resolve o problema de mensagens chegando fora de ordem devido a atrasos arbitrários na rede.
* **Multicast Totalmente Ordenado:** Utiliza Relógios de Lamport combinados com o ID do processo (para desempate) e uma fila de prioridade (`min-heap`).
* **Mecanismo de ACKs:** Mensagens só são entregues à camada de aplicação (tela do usuário) quando o processo tem a garantia (via recebimento de ACKs de todos os outros nós) de que nenhuma mensagem com timestamp anterior está em trânsito.
* **Simulação de Rede:** Utiliza a biblioteca `asyncio` para injetar latências assimétricas programadas entre os usuários.

### 2. Analisador de Causalidade (Relógios Vetoriais)
**Arquivo:** `relogios_vetoriais.py`

Uma ferramenta que orquestra e analisa eventos em um sistema distribuído para determinar a relação causal entre eles, superando a limitação dos Relógios de Lamport (que não conseguem distinguir eventos estritamente causais de eventos concorrentes).
* **Regras de Atualização:** Implementa a lógica vetorial (incremento local, _merge_ de vetores na recepção via valor máximo).
* **Análise Matemática:** Função `comparar_vetores(vc1, vc2)` que avalia se um evento "aconteceu antes", "aconteceu depois" ou se os eventos "são concorrentes".
* **Cenários de Teste:** O script roda automaticamente dois cenários simulados:
  * **Cenário 1:** Uma cadeia causal clara demonstrando o fluxo de informação.
  * **Cenário 2:** A ocorrência de eventos paralelos isolados, comprovando a concorrência temporal.

---

## 🚀 Pré-requisitos e Execução

O projeto foi desenvolvido em **Python 3** utilizando apenas bibliotecas nativas (`asyncio`, `heapq`, `logging`, `dataclasses`). Não é necessária a instalação de pacotes externos.

### Passos para rodar:

1. Clone ou faça o download deste repositório.
2. Abra o terminal de sua preferência e navegue até a pasta do projeto.
3. Recomenda-se o uso de um ambiente virtual:
   ```bash
   python -m venv .venv
   
   # Ativando no Windows:
   .venv\Scripts\activate
   
   # Ativando no Linux/macOS:
   source .venv/bin/activate
