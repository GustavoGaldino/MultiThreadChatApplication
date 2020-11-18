from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread

#Função que irá receber continuamente as mensagens enviadas pelo servidor
def receive():
    while True:
        try:
            msg = client_socket.recv(BUFSIZ).decode("utf8")
            print(msg)
        except OSError:
            exit()
            break

#Função que irá enviar as mensagens do cliente ao servidor
def send(event=None):
    msg = input()
    client_socket.send(bytes(msg, "utf8"))
    if msg == "bye":
        client_socket.close()
        exit()
    else:
        send()

#Entradas para determinar o ip e porta do servidor
HOST = input('Enter host: ')
PORT = input('Enter port: ')

if not PORT:
    PORT = 33000
else:
    PORT = int(PORT)

#Definindo algumas constantes que serão usadas ao longo do desenvolvimento do cliente
BUFSIZ = 1024
ADDR = (HOST, PORT)

client_socket = socket(AF_INET, SOCK_STREAM)
client_socket.connect(ADDR)

receive_thread = Thread(target=receive)
receive_thread.start()
send()