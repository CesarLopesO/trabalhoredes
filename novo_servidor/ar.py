import socket
import threading
import json

class ArCondicionado:
    def __init__(self):
        self.ligado = False
        self.temperatura = 20

    def ligar(self):
        self.ligado = True
        return "Ar condicionado ligado"

    def desligar(self):
        self.ligado = False
        return "Ar condicionado desligado"

    def verificar_estado(self):
        estado = "ligado" if self.ligado else "desligado"
        return f"Estado do ar condicionado: {estado}. Temperatura: {self.temperatura}°C"

    def mudar_temperatura(self, nova_temperatura):
        if 15 <= nova_temperatura <= 25:
            self.temperatura = nova_temperatura
            return f"Temperatura do ar condicionado alterada para {nova_temperatura}°C"
        else:
            return "Temperatura inválida"

    def salvar_configuracoes(self):
        configuracoes = {
            "ligado": self.ligado,
            "temperatura": self.temperatura
        }
        with open("ar_config.json", "w") as file:
            json.dump(configuracoes, file)

    def carregar_configuracoes(self):
        try:
            with open("ar_config.json", "r") as file:
                configuracoes = json.load(file)
                self.ligado = configuracoes.get("ligado", False)
                self.temperatura = configuracoes.get("temperatura", 20)
        except FileNotFoundError:
            self.salvar_configuracoes()
        except json.JSONDecodeError:
            self.salvar_configuracoes()

def handle_client(client_socket, ar):
    try:
        while True:
            data = client_socket.recv(1024)

            if not data:
                break

            print(f"[Servidor Ar] Recebido do Servidor Intermediário: {data.decode()}")

            # Processa os comandos do ar condicionado
            if data.decode() == "5":
                response = ar.ligar()
            elif data.decode() == "6":
                response = ar.desligar()
            elif data.decode() == "7":
                response = ar.verificar_estado()
            elif data.decode().startswith("temperatura"):
                nova_temperatura = int(data.decode().split()[1])
                response = ar.mudar_temperatura(nova_temperatura)
            elif data.decode().lower() == "exit":
                response = "Encerrando servidor Ar"
                break
            else:
                response = "Comando inválido"

            client_socket.send(response.encode())

    finally:
        ar.salvar_configuracoes()  # Salva configurações ao encerrar
        client_socket.close()

if __name__ == "__main__":
    ar_host = "127.0.0.1"
    ar_port = 8090

    ar_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ar_server.bind((ar_host, ar_port))
    ar_server.listen(5)

    print(f"[*] Servidor Ar ouvindo em {ar_host}:{ar_port}")

    ar = ArCondicionado()
    ar.carregar_configuracoes()  # Carrega as configurações ao iniciar

    try:
        while True:
            client_socket, addr = ar_server.accept()
            print(f"[*] Conexão recebida de {addr[0]}:{addr[1]}")

            client_handler = threading.Thread(target=handle_client, args=(client_socket, ar))
            client_handler.start()

    finally:
        print("[*] Servidor Ar encerrado.")
        ar_server.close()
