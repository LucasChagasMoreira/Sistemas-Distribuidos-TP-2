
from funcoesauxiliares import *
def node(node_id, next_node_port,ip, listen_port, node_service_name):

    request = [False,None]

    # Cria um socket para receber conexões
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.bind((node_service_name, listen_port))
    server_sock.listen()
    
    #socket para conectar com o proximo nó
    next_node_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    
    #iniciando thread para conectar com o proximo nó
    node_thread = threading.Thread(target=conectar_endereco, args=(next_node_sock,ip,next_node_port))
    node_thread.start()

    # Aceita conexão do nó anterior
    conn, addr = server_sock.accept()
    
    #espera o codigo conectar com o nó da frente
    node_thread.join()
    print(f"Nó {node_id} conectado ao nó anterior: {addr}")

    # Aceitar conexçao com o cliente
    print("Aguardando conexão com o cliente...")
    client_conn, client_addr = server_sock.accept()

    print(f"Cliente [Endereço: {client_addr}] conectou")
    print('Aguardando ID do cliente')
    id_client = receber_id(client_conn)
    print(f"ID {id_client} do cliente recebido")
    
    # Criando thread para tratar o client
    client_thread = threading.Thread(target=tratar_cliente, args=(client_conn,request))
    client_thread.start()

    if node_id == 1:
        initialdict ={id_client:request[1]}
        enviatoken(next_node_sock,initialdict)
        print("Token inicial enviado")

    while True:
        # Recebe a mensagem do nó anterior
        token = recebetoken(conn)
        
        print(f"Recebeu o token: {token}")
        time.sleep(0.3)

        # alocar espaço no token caso nao exista
        if id_client not in token:
            print(f"Alocando espaço no token")
            token[id_client] = request[1]

        # caso o meu timestamp seja o menor
        elif process_token(token,id_client):
            #acessar o recurso
            critic_acess_time = random.uniform(0.2, 1)


            print("Menor timestamp; acesso à região crítica")
            print(f"Entrando na região crítica [Tempo do sleep: {critic_acess_time:.2f} segundos]")
            acessar_regiao_critica()
            
            token[id_client] = None
            print(f"Escrevendo NULL na posição {node_id} no TOKEN")
            request[0] = False
            request[1] = None
        
        # caso nao tenha timestamp e o cliente esteja esperando uma mensagem
        elif request[0] == True and token[id_client] == None:
            token[id_client] = request[1]

        # se nao houver requisiçao nem nenhum timestamp no token, o token é passado para frente sem alteração
        # se houver requisiçao e o timestamp nao for o menor timestamp do token, o token é passado sem altera
        # Envia token para o próximo nó
        print(f"Enviando token para o proximo nó: [Endereço: {ip} e Porta: {next_node_port}]")
        
        enviatoken(next_node_sock,token)