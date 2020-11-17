from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread


def receive():
    while True:
        try:
            msg = client_socket.recv(BUFSIZ).decode("utf8")
            print(msg)
        except OSError:
            exit()
            break


def send(event=None):
    msg = input()
    client_socket.send(bytes(msg, "utf8"))
    if msg == "bye":
        client_socket.close()
        exit()
    else:
        send()

HOST = input('Enter host: ')
PORT = input('Enter port: ')
if not PORT:
    PORT = 33000
else:
    PORT = int(PORT)

BUFSIZ = 1024
ADDR = (HOST, PORT)

client_socket = socket(AF_INET, SOCK_STREAM)
client_socket.connect(ADDR)

receive_thread = Thread(target=receive)
receive_thread.start()
send()