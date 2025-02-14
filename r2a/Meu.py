from collections import deque




class D3SBAVS:#Dynamic Segment Size Selection in HTTP Based Adaptive Video Streaming ( Artigo o qual este código foi baseado)

    def __init__(self):
        
        self.throughput = deque(maxlen=5)
        self.M = len(self.throughput)
        

    # Função para calcular a variabilidade ponderada
    def variabilidade(self):
        print(f"lista que chegou no calculo de variabilidade é{self.throughput}")

        if self.M == 0:
            return 0  # Evita erro se a lista estiver vazia
        
        # Calcula a variabilidade ponderada
        self.mu = sum(self.throughput) / self.M
        sigma_weighted = sum((i / self.M) * abs(self.throughput[i] - self.mu) for i in range(self.M))

        return sigma_weighted

    # Função para calcular a probabilidade p
    def calcular_probabilidade(self):
        sigma2_weight = self.variabilidade()
        p = self.mu / (self.mu + sigma2_weight)
        print(f"Probabilidade é: {p}")
        return p

    # Função para calcular tau e theta
    def calcular_tau_theta_video(self, Q_current, Q):
        p = self.calcular_probabilidade()

        # Cálculo de τ e θ conforme descrito no artigo
        tau = (1 - p) * (Q_current - Q[max(0, Q_current - 1)])  # Aproxima do nível anterior
        theta = p * (Q[min(19, Q_current + 1)] - Q_current)  # Aproxima do próximo nível

        return tau, theta

    # Função para atualizar a qualidade de vídeo
    def atualizar_qualidade(self, Q_current, Qlist):
        # Verifica se throughput está vazio
        if len(self.throughput) == 0:
            print(self.throughput)
            Qnew = (int((len(Qlist) )/ 4) - 1) # decidido que começa pela qualidade de 1/4 da maxima, -1 pois começa em 0 e n 1
            print(Qnew)
            return Qnew  # Retorna 1/4 da qualidade quando throughput está vazio
        tau, theta = self.calcular_tau_theta_video(Q_current, Qlist)

        # Determinando nova qualidade com base em τ e θ
        Q_new = round(Q_current - tau + theta)  # Ajusta para o valor mais próximo válido
        Q_new = (max(0, min(19, Q_new)) )# Garante que fique dentro dos limites (0 a 19)
        print(Q_new)
        return Q_new

    def Atualiza_lista(self, Nova_lista):
        self.throughput = deque(Nova_lista)
        print(f"lista  recebida foi throughput é: {self.throughput}")