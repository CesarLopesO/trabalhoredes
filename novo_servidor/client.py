import socket


def main():
    intermediate_host = "127.0.0.1"
    intermediate_port = 9000

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((intermediate_host, intermediate_port))

        while True:
            print("\n------ Menu ------")
            print("1. Ligar Lâmpada")
            print("2. Desligar Lâmpada")
            print("3. Mudar cor da Lâmpada ")
            print("4. Verificar Status da Lâmpada")
            print("5. Ligar Ar Condicionado")
            print("6. Desligar Ar Condicionado")
            print("7. Verificar Status do Ar Condicionado")
            print("8. Mudar Temperatura do Ar Condicionado")
            print("exit. Sair")

            command = input("Digite o número do comando ou 'exit' para sair: ")

            if command.lower() == "exit":
                client_socket.sendall(command.encode())
                break

            # Adicionando a opção de mudar a temperatura do ar condicionado
            if command == "8":
                nova_temperatura = input("Digite a nova temperatura do ar condicionado: ")
                command = f"temperatura {nova_temperatura}"
            elif command =="3":
                nova_cor =input("Digite a nova cor da Lâmpada: ")
                command=f"cor {nova_cor}"

            client_socket.sendall(command.encode())
            response = client_socket.recv(1024)
            print(f"[Cliente] Recebido do Servidor Intermediário: {response.decode()}")


if __name__ == "__main__":
    main()
