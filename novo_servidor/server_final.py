import socket
import threading
import json

class Lampada:
    def __init__(self):
        self.estado = "desligada"
        self.cor = "white"

    def ligar(self):
        self.estado = "ligada"
        return f"Lâmpada ligada. Cor: {self.cor}"

    def desligar(self):
        self.estado = "desligada"
        return "Lâmpada desligada"

    def verificar_estado(self):
        return f"Estado da lâmpada: {self.estado}. Cor: {self.cor}"

    def mudar_cor(self, cor):
        cores_validas = ["red", "green", "blue", "yellow","white"]
        if cor in cores_validas:
            self.cor = cor
            return f"Cor da lâmpada alterada para {cor}"
        else:
            return "Cor inválida"

    def salvar_configuracoes(self):
        configuracoes = {
            "estado": self.estado,
            "cor": self.cor
        }
        with open("config.json", "w") as file:
            json.dump(configuracoes, file)

    def carregar_configuracoes(self):
        try:
            with open("config.json", "r") as file:
                configuracoes = json.load(file)
                self.estado = configuracoes.get("estado", "desligada")
                self.cor = configuracoes.get("cor", "white")
        except FileNotFoundError:
            self.salvar_configuracoes()
        except json.JSONDecodeError:
            self.salvar_configuracoes()

def handle_client(client_socket, lampada):
    try:
        while True:
            data = client_socket.recv(1024)

            if not data:
                break

            print(f"[Servidor Final] Recebido do Servidor Intermediário: {data.decode()}")

            # Processa os comandos da lâmpada
            if data.decode() == "1":
                response = lampada.ligar()
            elif data.decode() == "2":
                response = lampada.desligar()
            elif data.decode() == "4":
                response = lampada.verificar_estado()
            elif data.decode().startswith("cor"):
                cor_desejada = data.decode().split()[1]
                response = lampada.mudar_cor(cor_desejada)
            elif data.decode().lower() == "exit":
                response = "Encerrando servidor final"
                break
            else:
                response = "Comando inválido"

            client_socket.send(response.encode())

    finally:
        lampada.salvar_configuracoes()  # Salva configurações ao encerrar
        client_socket.close()

if __name__ == "__main__":
    final_host = "127.0.0.1"
    final_port = 8080

    final_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    final_server.bind((final_host, final_port))
    final_server.listen(5)

    print(f"[*] Servidor final ouvindo em {final_host}:{final_port}")

    lampada = Lampada()
    lampada.carregar_configuracoes()  # Carrega as configurações ao iniciar

    try:
        while True:
            client_socket, addr = final_server.accept()
            print(f"[*] Conexão recebida de {addr[0]}:{addr[1]}")

            client_handler = threading.Thread(target=handle_client, args=(client_socket, lampada))
            client_handler.start()

    finally:
        print("[*] Servidor final encerrado.")
        final_server.close()
