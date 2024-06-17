import tkinter as tk
from tkinter import ttk
import socket
import threading
import time

class ClienteGUI:
    def __init__(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect(("127.0.0.1", 9000))

        self.ar_condicionado_ligado = False
        self.lampada_ligada = False
        self.temperatura_ar = ""
        self.cor_lampada = self.obter_cor_inicial()

        # Iniciar a interface gráfica
        self.app = tk.Tk()
        self.app.title("Cliente")

        self.frame_ar_condicionado = ttk.LabelFrame(self.app, text="Ar-Condicionado")
        self.frame_ar_condicionado.pack(padx=10, pady=10)

        self.btn_ar_condicionado = ttk.Button(self.frame_ar_condicionado, text="Ligar/Desligar", command=self.toggle_ar_condicionado)
        self.btn_ar_condicionado.grid(row=0, column=0)

        self.label_ar_condicionado = ttk.Label(self.frame_ar_condicionado, text=f"Ar: {'Desligado' if self.ar_condicionado_ligado else 'Ligado'}")
        self.label_ar_condicionado.grid(row=0, column=1)

        self.frame_temperatura = ttk.LabelFrame(self.frame_ar_condicionado, text="")
        self.frame_temperatura.grid(row=1, column=0, columnspan=2, pady=5)

        # Use o ttk.Spinbox para a entrada da temperatura
        self.spinbox_temperatura_ar = ttk.Spinbox(self.frame_temperatura, from_=15, to=25, wrap=True, state="readonly", command=self.alterar_temperatura)
        self.spinbox_temperatura_ar.set(self.temperatura_ar)
        self.spinbox_temperatura_ar.grid(row=0, column=0)

        self.label_temperatura = ttk.Label(self.frame_temperatura, text="Temperatura")
        self.label_temperatura.grid(row=0, column=1)

        self.frame_lampada = ttk.LabelFrame(self.app, text="Lâmpada")
        self.frame_lampada.pack(padx=10, pady=10)

        self.btn_lampada = ttk.Button(self.frame_lampada, text="Ligar/Desligar", command=self.toggle_lampada)
        self.btn_lampada.grid(row=0, column=0)

        self.label_lampada = ttk.Label(self.frame_lampada, text=f"Lâmpada: {'Ligada' if self.lampada_ligada else 'Desligada'}, Cor: {self.cor_lampada}")
        self.label_lampada.grid(row=0, column=1)

        self.frame_cor_lampada = ttk.LabelFrame(self.frame_lampada, text="Cor da Lâmpada")
        self.frame_cor_lampada.grid(row=1, column=0, columnspan=2, pady=5)

        cores_lampada = ["red", "green", "blue", "yellow", "white"]
        self.combobox_cor_lampada = ttk.Combobox(self.frame_cor_lampada, values=cores_lampada, state="readonly")
        self.combobox_cor_lampada.set(self.cor_lampada)
        self.combobox_cor_lampada.grid(row=0, column=0)

        self.btn_alterar_cor_lampada = ttk.Button(self.frame_cor_lampada, text="Alterar", command=self.alterar_cor_lampada)
        self.btn_alterar_cor_lampada.grid(row=0, column=1)

        # Adicione um botão "Salvar e Sair"
        self.btn_salvar_sair = ttk.Button(self.app, text="Salvar e Sair", command=self.salvar_e_sair)
        self.btn_salvar_sair.pack(pady=10)

        # Iniciar a thread para atualizar automaticamente o status
        self.thread_status = threading.Thread(target=self.atualizar_status)
        self.thread_status.start()

        self.app.mainloop()

    def obter_status_inicial(self):
        # Solicitar o status do ar condicionado (comando 7)
        self.client_socket.sendall("7".encode())
        resposta_ar = self.client_socket.recv(1024).decode()

        # Analisar a resposta e atualizar o status do ar condicionado
        if "Ar: Ligado" in resposta_ar:
            self.ar_condicionado_ligado = True
        else:
            self.ar_condicionado_ligado = False

        # Solicitar o status da lâmpada (comando 4)
        self.client_socket.sendall("4".encode())
        resposta_lampada = self.client_socket.recv(1024).decode()

        # Analisar a resposta e atualizar o status da lâmpada e a cor
        if "Lâmpada: Ligada" in resposta_lampada:
            self.lampada_ligada = True
        else:
            self.lampada_ligada = False

        if "Cor da Lâmpada" in resposta_lampada:
            cor = resposta_lampada.split(":")[-1].strip()
            self.cor_lampada = cor
        else:
            self.cor_lampada = "Escolha a cor"

        print(f"Ar: {self.ar_condicionado_ligado}, Lâmpada: {self.lampada_ligada}, Cor: {self.cor_lampada}")

    def obter_cor_inicial(self):
        # Solicitar o status da lâmpada (comando 4)
        self.client_socket.sendall("4".encode())
        resposta_lampada = self.client_socket.recv(1024).decode()

        # Analisar a resposta e obter a cor da lâmpada
        if "Cor da Lâmpada" in resposta_lampada:
            return resposta_lampada.split(":")[-1].strip()
        else:
            return "Escolha a cor"

    def atualizar_status(self):
        while True:
            # Atualize os elementos da interface gráfica conforme necessário
            self.label_ar_condicionado.config(text=f"Ar: {'Desligado' if self.ar_condicionado_ligado else 'Ligado'}")
            self.label_lampada.config(text=f"Lâmpada: {'Ligada' if self.lampada_ligada else 'Desligada'}, Cor: {self.cor_lampada}")
            time.sleep(1)

    def toggle_ar_condicionado(self):
        comando = "5" if self.ar_condicionado_ligado else "6"
        resposta = self.enviar_comando(comando)
        self.ar_condicionado_ligado = not self.ar_condicionado_ligado

    def toggle_lampada(self):
        comando = "2" if self.lampada_ligada else "1"
        resposta = self.enviar_comando(comando)
        self.lampada_ligada = not self.lampada_ligada

    def alterar_temperatura(self):
        nova_temperatura = int(self.spinbox_temperatura_ar.get())
        comando = f"temperatura {nova_temperatura}"
        resposta = self.enviar_comando(comando)
        self.temperatura_ar = nova_temperatura

    def alterar_cor_lampada(self):
        nova_cor = self.combobox_cor_lampada.get()
        comando = f"cor {nova_cor.lower()}"
        resposta = self.enviar_comando(comando)
        self.cor_lampada = nova_cor

    def salvar_e_sair(self):
        comando = "exit"
        resposta = self.enviar_comando(comando)
        # Aguarde um curto período antes de encerrar o aplicativo
        time.sleep(1)
        self.client_socket.close()
        self.app.destroy()

    def enviar_comando(self, comando):
        try:
            self.client_socket.send(comando.encode())
            resposta = self.client_socket.recv(1024).decode()
            return resposta
        except Exception as error:
            return f"Erro: {error}"

if __name__ == "__main__":
    cliente_gui = ClienteGUI()
