


# Nome do Arquivo: R2A_D3SBAVS.py
# Aplicação: Trabalho  CIC0124 - REDES DE COMPUTADORES - Turma 02 - 2024/2 - Marcos Fagundes Caetano 
# Autor: Gustavo Falcomer Pontes Viégas 
# Matrícula : 190042800
# Data de Criação: 2025-01-28
# Última Modificação: 2025-02-13
# Versão: 2.0
# Descrição: Controle de qualidade de streaming de video baseado no artigo Dynamic Segment Size Selection in HTTP Based Adaptive Video Streaming (D3SBAVS)

from r2a.ir2a import IR2A
from player.parser import *
import time
from statistics import mean
from collections import deque
from typing import Any 


















class R2A_D3sbavs(IR2A):

    def __init__(self, id):
      
        IR2A.__init__(self, id)
        self.TLS = 5
        self.throughputs = deque(maxlen=5)
        self.request_time = 0
        self.qi = []
        self.Q_current = 0 #armazena valor atual da qualidade
        self.Q_control = D3SBAVS(self.TLS) # cria instancia do codigo de decisão

    def handle_xml_request(self, msg):
        
        self.request_time = time.perf_counter()
        self.send_down(msg)

    def handle_xml_response(self, msg):
        
        parsed_mpd = parse_mpd(msg.get_payload())
        self.qi = parsed_mpd.get_qi()
   

        t = time.perf_counter() - self.request_time
        self.throughputs.append(msg.get_bit_length()/t)
        

        self.send_up(msg)

    def handle_segment_size_request(self, msg):
        
        self.request_time = time.perf_counter()
    
        self.Q_control.Atualiza_lista(self.throughputs)
        
        selected_qi = self.Q_control.atualizar_qualidade(self.Q_current, self.qi)
        self.Q_current = selected_qi
        msg.add_quality_id(self.qi[selected_qi])
        self.send_down(msg)

    def handle_segment_size_response(self, msg):
        
        t = time.perf_counter() - self.request_time
        self.throughputs.append(msg.get_bit_length() / t)
       
        self.send_up(msg)

    def initialize(self):
        pass

    def finalization(self):
        pass

class D3SBAVS:#Dynamic Segment Size Selection in HTTP Based Adaptive Video Streaming ( Artigo o qual este código foi baseado)

    def __init__(self, tamanho):
        TLS= tamanho
        self.throughput = deque(maxlen=TLS)
        
        

    # Função para calcular a variabilidade ponderada
    def variabilidade(self):
        

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
        print(f"Probabilidade é: {p}\n")
        return p

    # Função para calcular tau e theta
    def calcular_tau_theta_video(self, Q_current, Q):
        p = self.calcular_probabilidade()

        # Cálculo de τ e θ conforme descrito no artigo
        tau = (1 - p) * (Q_current - Q[max(0, Q_current - 1)])  # Aproxima do nível anterior
        theta = p * (Q[min(19, Q_current + 1)] - Q_current)  # Aproxima do próximo nível
        print(f"tau é: {tau}\n")
        print(f"theta e :{theta}")
        return  tau, theta

    # Função para atualizar a qualidade de vídeo
    def atualizar_qualidade(self, Q_current, Qlist):
        # Verifica se throughput está vazio
        Q_quali=list(range(len(Qlist)))
        tau, theta = self.calcular_tau_theta_video(Q_current, Q_quali)

        # Determinando nova qualidade com base em τ e θ
        Q_new = round(Q_current - tau + theta)  # Ajusta para o valor mais próximo válido
        Q_new = (max(0, min(19, Q_new)) )# Garante que fique dentro dos limites (0 a 19)
        return Q_new

    def Atualiza_lista(self, Nova_lista):
        self.throughput = deque(Nova_lista)
        self.M = len(self.throughput)
        self.mu = sum(self.throughput) / self.M
        print(f"banana: {self.throughput}\n")
