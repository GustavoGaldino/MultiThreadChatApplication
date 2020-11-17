from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
from datetime import datetime

def aceitar_conexoes():
    while True:
        cliente, endereco_cliente = SERVER.accept()
        print("%s:%s conectou." % endereco_cliente)
        cliente.send(bytes("Bem-vindo! Digite seu nome e aperte ENTER", "utf8"))
        Thread(target=atender_cliente, args=(cliente,)).start()

def atender_cliente(cliente):
    nome = ""
    while not nome:
        nome = cliente.recv(BUFSIZ).decode("utf8")
        if nome in clientes.values():
            print(nome + " já está em uso.")
            nome = ""
            cliente.send(bytes("Esse nome já esta em uso, escolha outro nome!","utf8"))
    print("Novo usuário: " + nome)
    welcome_messages = [
        "Bem-vindo, %s! Se você, em algum momento, desejar se desconectar, digite bye"%nome,
        "Caso queira enviar uma mensagem para todos, digite send -all seguido da mensagem\n",
        "Caso queira enviar uma mensagem para um usuario especifico, digita send -user [nome do usuario] seguido da mensagem\n",
        "Caso queira uma lista dos usuarios presentes, digite list\n"
    ]
    for msg in welcome_messages:
        cliente.send(bytes(msg, "utf8"))
    msg = "%s se juntou ao chat!" % nome
    broadcast(bytes(msg, "utf8"))
    clientes[cliente] = nome

    while True:
        msg = cliente.recv(BUFSIZ)
        msg = msg.decode("utf8")
        msg = msg.split()
        print(msg)
        if msg[0] == "send":
            if msg[1] == "-all":
                client_ip = None
                client_port = None
                msg_content = ""
                for i in range(2, len(msg)):
                    msg_content += (msg[i] + " ")
                for sockets in clientes.keys():
                    if clientes[sockets] == nome:
                        client_ip, client_port = sockets.getpeername()
                dt_string = datetime.now().strftime("%d/%m/%Y %H:%M:%S")	
                broadcast(bytes(client_ip + ':' + str(client_port) + '/~' + nome + ": " + msg_content + dt_string, "utf8"))
            elif msg[1] == "-user":
                if msg[2] in clientes.values():
                    client_socket = None
                    client_ip = None
                    client_port = None
                    msg_content = ""
                    for i in range(3, len(msg)):
                        msg_content += (msg[i] + " ")
                    for sockets in clientes.keys():
                        if clientes[sockets] == nome:
                            client_ip, client_port = sockets.getpeername()
                        if clientes[sockets] == msg[2]:
                            client_socket = sockets
                    dt_string = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                    cliente.send(bytes("/~Você: " + msg_content + " " + dt_string, "utf8"))	
                    client_socket.send(bytes(client_ip + ':' + str(client_port) + '/~' +  nome + ": " + msg_content + " " + dt_string, "utf8"))
                else:
                    temp = "Usuario nao existente!"
                    cliente.send(bytes(temp, "utf8"))
            else:
                temp = "Comando invalido"
                cliente.send(bytes(temp, "utf8"))
        elif msg[0] == "list":
            temp = "Usuarios disponiveis:"
            for cur_socket in clientes.keys():
                temp = temp + " %s" % clientes[cur_socket]
            cliente.send(bytes(temp, "utf8"))
        elif msg[0] == "bye":
            cliente.send(bytes("Você foi desconectado!!", "utf8"))
            cliente.close()
            del clientes[cliente]
            broadcast(bytes("%s saiu do chat" % nome, "utf8"))
            break
        else:
            cliente.send(bytes("Comando inválido!", "utf8"))

def broadcast(msg, prefixo=""):

    for socket in clientes:
        socket.send(bytes(prefixo, "utf8")+msg)

clientes = {}

HOST = ''
PORT = 32000
BUFSIZ = 1024
ADDR = (HOST, PORT)

SERVER = socket(AF_INET, SOCK_STREAM)
SERVER.bind(ADDR)

if __name__ == "__main__":
    SERVER.listen(5)
    print("Aguardando conexao...")
    ACCEPT_THREAD = Thread(target=aceitar_conexoes)
    ACCEPT_THREAD.start()
    ACCEPT_THREAD.join()
    SERVER.close()