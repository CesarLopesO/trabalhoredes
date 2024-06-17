import socket
import threading

class IntermediateServer:
    def __init__(self, final1_host, final1_port, final2_host, final2_port):
        self.final1_host = final1_host
        self.final1_port = final1_port
        self.final2_host = final2_host
        self.final2_port = final2_port

    def start_server(self):
        intermediate_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        intermediate_server.bind(("127.0.0.1", 9000))
        intermediate_server.listen(5)

        print(f"[*] Servidor intermediário ouvindo em 127.0.0.1:9000")

        while True:
            client_socket, addr = intermediate_server.accept()
            print(f"[*] Conexão recebida de {addr[0]}:{addr[1]}")

            client_handler = threading.Thread(target=self.handle_client, args=(client_socket,))
            client_handler.start()

    def handle_client(self, client_socket):
        try:
            while True:
                data = client_socket.recv(1024)

                if not data:
                    break

                print(f"[Servidor Intermediário] Recebido do Cliente: {data.decode()}")

                # Determina qual servidor final acessar com base na mensagem recebida
                if data.decode() == "1" or data.decode() == "2" or data.decode() == "4":
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as final_socket:
                        final_socket.connect((self.final1_host, self.final1_port))
                        final_socket.sendall(data)
                        final_response = final_socket.recv(1024)

                    print(f"[Servidor Intermediário] Recebido do Servidor Final: {final_response.decode()}")
                    client_socket.send(final_response)
                elif data.decode().startswith("cor"):
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as final_socket:
                        final_socket.connect((self.final1_host, self.final1_port))
                        final_socket.sendall(data)
                        final_response = final_socket.recv(1024)

                    print(f"[Servidor Intermediário] Recebido do Servidor Final: {final_response.decode()}")
                    client_socket.send(final_response)
                elif data.decode() == "5" or data.decode() == "6" or data.decode() == "7":
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as ar_socket:
                        ar_socket.connect((self.final2_host, self.final2_port))
                        ar_socket.sendall(data)
                        ar_response = ar_socket.recv(1024)

                    print(f"[Servidor Intermediário] Recebido do Servidor Ar: {ar_response.decode()}")
                    client_socket.send(ar_response)
                elif data.decode().startswith("temperatura"):
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as ar_socket:
                        ar_socket.connect((self.final2_host, self.final2_port))
                        ar_socket.sendall(data)
                        ar_response = ar_socket.recv(1024)

                    print(f"[Servidor Intermediário] Recebido do Servidor Ar: {ar_response.decode()}")
                    client_socket.send(ar_response)
                elif data.decode().lower() == "exit":
                    response = "Encerrando servidor intermediário"
                    client_socket.send(response.encode())
                    break
                else:
                    response = "Comando inválido"
                    client_socket.send(response.encode())

        finally:
            client_socket.close()

if __name__ == "__main__":
    final1_host = "127.0.0.1"
    final1_port = 8080
    final2_host = "127.0.0.1"
    final2_port = 8090

    intermediate_server = IntermediateServer(final1_host, final1_port, final2_host, final2_port)
    intermediate_server.start_server()
