from funcoesauxiliares import *

def start(node_port,node_ip,primarynode_port,primarynode_ip):
    flag = threading.Event()
    registro = []
    permição = threading.Event()
    permição.set()
    #socket para receber conexoes
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.bind((node_ip,node_port))
    server_sock.listen()

    address, port = server_sock.getsockname()
    print(f"porta do nó: {port}, ip: {address}")
    #socket para conexão com o no primario
    primary_node_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print({primary_node_sock})

    #connectando com o nó primario
    connect_primary_node(primary_node_sock,primarynode_port,primarynode_ip)
    
    #thread para lidar com a conexão com o nó primario
    node_thread = threading.Thread(target=primary_connection, args=(primary_node_sock,registro,flag,permição))
    node_thread.start()

    while(True):
        # Aceita conexão com algum elemento do cluster sync qualquer
        try:
            # Aceita conexão com algum elemento do cluster sync qualquer
            print("esperando cliente...")
            conn, addr = server_sock.accept()
            print(f"Conexão estabelecida com {addr}")
            
            # Recebe a mensagem
            #print("esperando threads permitirem conexao")
            permição.wait()
            mensagem = receber_estrutura(conn)
            print("requisição do cliente recebida.")
            requisicao, dado = pickle.loads(mensagem)

            #erro: cluster cai com pedido do cliente
            if dado == 3:
                primary_node_sock.close()
                print("DESCONECTEI, ERRO 3")
                return
            
            # mensagem = (requisição de leitura/escrita, dado)
            # dado = (endereço do cliente, inteiro)
            if requisicao == "R":
                resultado = buscar(dado, registro)
                # Retorna o resultado da leitura
                conn.sendall(str(resultado).encode('utf-8'))
            
            elif requisicao == "W":
                # Coloca a flag em 0 para simbolizar que os dados não estão atualizados
                
                # Envia o dado para o nó primário e aguarda atualização
                dado_serializado = pickle.dumps(dado)
                
                if dado not in registro:
                    print("enviando requisição para o primario")
                    primary_node_sock.send(dado_serializado)
                    #print(f"dado enviado: {dado_serializado}")
                    #enviar_estrutura(primary_node_sock, dado)

                    
                    # Aguarda até que a flag seja alterada para 1 (significando que os dados foram atualizados)
                    print("esperando notificação de atualizaçao do primario...")
                    flag.wait()
                    print("notificando o cliente")
                    conn.sendall("Escrita feita!!".encode('utf-8'))
                    print(f'registro atual: {registro}')
                    flag.clear()

                    #erro: cluster cai sem estar fazendo nada
                    if dado == 1:
                         primary_node_sock.close()
                         print("DESCONECTEI, ERRO 1")
                         return
                else:
                    print("notificando o cliente")
                    conn.sendall("Escrita feita!!".encode('utf-8'))
                    print(f'registro atual: {registro}')
                    #erro: cluster cai sem estar fazendo nada
                    if dado == 1:
                         primary_node_sock.close()
                         print("DESCONECTEI, ERRO 1")
                         return
                # Retorna ao cliente a confirmação da escrita
        except Exception as e:
            print(f"Erro durante a comunicação: {e}")
        finally:
            # Garante que a conexão será fechada ao final
            conn.close()
            print(f"Conexão com {addr} foi fechada.")
         

