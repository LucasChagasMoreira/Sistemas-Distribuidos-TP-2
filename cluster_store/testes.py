from funcoesauxiliares import *


portasla1 = 56799
portasla2 = 56802
PORTAS = [16008,16001,16004]
i = 0

while True:
    porta = random.choice(PORTAS)
    comando = random.choice(["W","R"])
    
    valor = random.randint(0, 15)
    

    # Criar um socket para o cliente
    cliente_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cliente_socket.settimeout(5.0)
    try:
        cliente_socket.connect(('localhost', porta))
    except Exception as e:
        print(f"cluster : {porta} caiu")
        
    # Preparar a requisição (escrita ou leitura)
    requisicao = (comando,(valor))
    print(f'enviando requisição: {requisicao},para porta: {porta}')


    requisicao = pickle.dumps(requisicao)
    try:
        enviar_estrutura(cliente_socket,requisicao)

        resposta = cliente_socket.recv(2048).decode('utf-8')
        print(f"Resposta do servidor na porta {porta}: {resposta}")

    except Exception as e:
        print(f"cluster : {porta} caiu")
        PORTAS.remove(porta)
        
    
    #resposta = receber_mensagem(cliente_socket)
    
    cliente_socket.close()
    time.sleep(0.3)
    i += 1