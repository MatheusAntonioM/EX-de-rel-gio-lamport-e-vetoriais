class Processo:
    """
    Representa um processo no sistema distribuído com seu próprio Relógio Vetorial.
    """
    def __init__(self, pid, num_processos):
        self.pid = pid
        self.num_processos = num_processos
        # Inicializa o relógio vetorial com zeros para os N processos: [0, 0, ..., 0]
        self.vc = [0] * num_processos

    def evento_interno(self):
        """
        Regra 1: Incrementa o relógio local para um evento interno.
        """
        self.vc[self.pid] += 1
        return list(self.vc) # Retorna uma cópia do estado atual do relógio

    def evento_envio(self):
        """
        Regra 1: O envio de uma mensagem também é um evento que incrementa o tempo local.
        """
        self.vc[self.pid] += 1
        return list(self.vc)

    def evento_recebimento(self, ts_msg):
        """
        Regra 2: Na recepção, o processo atualiza seu vetor pegando o máximo 
        entre o seu valor atual e o valor recebido na mensagem, e depois incrementa seu próprio ID.
        """
        for k in range(self.num_processos):
            self.vc[k] = max(self.vc[k], ts_msg[k])
        
        # Após sincronizar com a mensagem, incrementa o próprio relógio (o recebimento é um evento)
        self.vc[self.pid] += 1
        return list(self.vc)


def comparar_vetores(vc1, vc2):
    """
    Compara dois relógios vetoriais e retorna a relação de causalidade entre eles.
    """
    # Verifica se vc1 <= vc2 em TODAS as posições
    menor_ou_igual = all(v1 <= v2 for v1, v2 in zip(vc1, vc2))
    # Verifica se vc1 < vc2 em PELO MENOS UMA posição
    estritamente_menor = any(v1 < v2 for v1, v2 in zip(vc1, vc2))
    
    # Verifica se vc1 >= vc2 em TODAS as posições
    maior_ou_igual = all(v1 >= v2 for v1, v2 in zip(vc1, vc2))
    # Verifica se vc1 > vc2 em PELO MENOS UMA posição
    estritamente_maior = any(v1 > v2 for v1, v2 in zip(vc1, vc2))

    # Regras de Causalidade dos Relógios Vetoriais
    if menor_ou_igual and estritamente_menor:
        return "aconteceu antes de"
    elif maior_ou_igual and estritamente_maior:
        return "aconteceu depois de"
    else:
        # Se um não é estritamente menor nem maior que o outro, não há caminho causal
        return "são concorrentes"


def main():
    print("="*50)
    print("SIMULADOR DE RELÓGIOS VETORIAIS E CAUSALIDADE")
    print("="*50)

    # Inicializando um sistema com 3 processos (N=3)
    N = 3
    P0 = Processo(0, N)
    P1 = Processo(1, N)
    P2 = Processo(2, N)

    # ---------------------------------------------------------
    # CENÁRIO 1: Cadeia Causal (A -> B)
    # ---------------------------------------------------------
    print("\n[ CENÁRIO 1: Cadeia Causal ]")
    
    # Processo 0 executa um evento interno
    evento_A = P0.evento_interno()
    print(f"-> P0 executou 'Evento A'. \n   Vetor resultante: {evento_A}")
    
    # Processo 0 envia uma mensagem para Processo 1
    ts_envio_P0 = P0.evento_envio()
    print(f"-> P0 enviou mensagem para P1. \n   Vetor anexado à msg: {ts_envio_P0}")
    
    # Processo 1 recebe a mensagem de Processo 0
    evento_B = P1.evento_recebimento(ts_envio_P0)
    print(f"-> P1 recebeu a mensagem (executou 'Evento B'). \n   Vetor resultante: {evento_B}")
    
    # Analisando a relação entre Evento A e Evento B
    resultado_causal = comparar_vetores(evento_A, evento_B)
    print("-" * 30)
    print(f"CONCLUSÃO: O Evento A {resultado_causal} Evento B.")
    print("-" * 30)


    # ---------------------------------------------------------
    # CENÁRIO 2: Eventos Concorrentes (X || Y)
    # ---------------------------------------------------------
    print("\n[ CENÁRIO 2: Eventos Concorrentes ]")
    
    # Processo 1 executa um evento interno (totalmente independente do P2)
    evento_X = P1.evento_interno()
    print(f"-> P1 executou 'Evento X'. \n   Vetor resultante: {evento_X}")
    
    # Processo 2 executa um evento interno (totalmente independente do P1)
    evento_Y = P2.evento_interno()
    print(f"-> P2 executou 'Evento Y'. \n   Vetor resultante: {evento_Y}")
    
    # Analisando a relação entre Evento X e Evento Y
    resultado_concorrencia = comparar_vetores(evento_X, evento_Y)
    print("-" * 30)
    
    if resultado_concorrencia == "são concorrentes":
        print(f"CONCLUSÃO: O Evento X e o Evento Y {resultado_concorrencia}.")
    else:
        print(f"CONCLUSÃO: O Evento X {resultado_concorrencia} Evento Y.")
    print("-" * 30)
    print("\nFim da simulação.\n")


if __name__ == "__main__":
    main()
