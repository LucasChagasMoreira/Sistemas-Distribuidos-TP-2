import socket
import threading
import time
import pickle
import random
from funcoesauxiliares import enviar_mensagem,receber_mensagem,enviar_estrutura,receber_estrutura

def cliente(id,ip,node_port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((ip,node_port))
    print(f"Conectado ao elemento {id} do ClusterSync na porta:{node_port}")

    # enviando id
    print(f"Enviando ID: {id}")
    enviar_mensagem(sock,id)
    # definindo quantidade de requests
    requests_number = random.randint(10,20)

    for i in range(requests_number):
        # enviando time stamp
        timestamp = time.time()
        print(f"Enviando Requisição para o Elemento do ClusterSync [Timestamp: {timestamp:.2f}]")
        timestamp = pickle.dumps(timestamp)
        enviar_estrutura(sock, timestamp)
        print(f"Requisição enviada")
        # esperando mensagem de commit
        resposta = receber_mensagem(sock)
        
        print(f'Recebeu resposta do elemento do ClusterSync: {resposta}')
        time_sleep = random.randint(1,5)
        print(f"Dormindo por {time_sleep} segundos antes de enviar nova requisição")
        time.sleep(time_sleep)
    
    print(f"Desconectando do elemento do ClusterSync [Endereço: {ip} e porta: {node_port}]")        

