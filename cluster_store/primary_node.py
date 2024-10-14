from funcoesauxiliares import *
def start(node_port,node_ip):
    
    #estabelecer conexão com seus outros nos
    registro = []
    backup1 = threading.Event()
    backup2 = threading.Event()
    permissão1 = threading.Event()
    permissão2 = threading.Event()
    permissão1.set()
    permissão2.set()
    connections = []
    flag_communicação = threading.Event()
    #socket para receber conexoes
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.bind((node_ip, node_port))
    server_sock.listen()

    print('esperando conexoes do no 1')
    node_sock1, node_addr1 = server_sock.accept()
    connections.append(node_sock1)
    client_thread = threading.Thread(target=backup_connection, args=(node_sock1,registro,connections,backup1,flag_communicação,permissão1))
    client_thread.start()

    print('esperando conexoes do no 2')
    node_sock2, node_addr2 = server_sock.accept()
    connections.append(node_sock2)
    client_thread = threading.Thread(target=backup_connection, args=(node_sock2,registro,connections,backup2,flag_communicação,permissão2))
    client_thread.start()

    #esperar receber alguma requsição
    while True:
        try:
            print("esperando cliente...")
            client_sock,client_addr = server_sock.accept()
            print(f"Conexão estabelecida com {client_addr}")

            print("esperando threads permitirem conexao")
            permissão1.wait()
            permissão2.wait()
            mensagem = receber_estrutura(client_sock)
            print("recebi a estrutura")
            requisicao, dado = pickle.loads(mensagem)

            # mensagem = (requisição de leitura/escrita, dado)
            # dado = (endereço do cliente, inteiro)
            if requisicao == "R":
                resultado = buscar(dado, registro)
                # Retorna o resultado da leitura
                client_sock.send(str(resultado).encode('utf-8'))

            #caso de escrita
            elif requisicao == "W":
                #caso o dado nao esteja presente nos registros
                if dado not in registro:
                    #colaca os dados no registro
                    registro.append(dado)
                    #serializa os dados
                    dado_serializado = pickle.dumps(dado)

                    #itera sobre todas suas conexões com os outros nós
                    for conn in connections:
                        #envia os dados para todos os nós
                        conn.sendall(dado_serializado)
                        print(f"mensagem thread: enviando: {dado} tipo: {type(dado)}")
                    
                    print("esperando...")
                    while not (backup1.is_set() and backup2.is_set()):
                        
                        time.sleep(0.1)
                    
                    backup1.clear()
                    backup2.clear()

                    print("todos os backups atualizados!!") 
                    client_sock.sendall("Escrita feita!!".encode('utf-8'))
                    print(f'registro atual: {registro}')
                    
                else:
                    client_sock.sendall("Escrita feita!!".encode('utf-8'))
                    print(f'registro atual: {registro}')

        except Exception as e:
            print(f"Erro durante a comunicação: {e}")
        finally:
            # Garante que a conexão será fechada ao final
            client_sock.close()
            print(f"Conexão com {client_addr} foi fechada.")

