from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
from datetime import datetime

#Função que irá receber continuamente as tentativas de conexão por parte do usuário:
def aceitar_conexoes():
    while True:
        cliente, endereco_cliente = SERVER.accept()
        print("%s:%s conectou." % endereco_cliente)
        #Ao captar uma conexão, o servidor irá enviar uma mensagem de boas vindas requisitando o nome do usuário:
        cliente.send(bytes("Bem-vindo! Digite seu nome e aperte ENTER", "utf8"))
        #Também será criado uma nova thread para o novo usuário através do seu socket:
        Thread(target=atender_cliente, args=(cliente,)).start()

#Função que irá receber o nome e as mensagens enviadas pelo usuário e irá diferenciar cada comando proveniente das mensagens:
def atender_cliente(cliente):
    nome = ""
    #Laço que irá verificar se o nome já existe no dicionário de clientes e irá requisitar outro nome caso já exista:
    while not nome:
        nome = cliente.recv(BUFSIZ).decode("utf8")
        if nome in clientes.values():
            print(nome + " já está em uso.")
            nome = ""
            cliente.send(bytes("Esse nome já esta em uso, escolha outro nome!","utf8"))
    print("Novo usuário: " + nome)

    #Mensagem recebida pelo usuário no momento em que ele se conectar ao chat:
    welcome_messages = """
        Bem-vindo, %s! Se você, em algum momento, desejar se desconectar, digite bye,
        Caso queira enviar uma mensagem para todos, digite send -all seguido da mensagem\n,
        Caso queira enviar uma mensagem para um usuario especifico, digita send -user [nome do usuario] seguido da mensagem\n,
        Caso queira uma lista dos usuarios presentes, digite list\n
    """ %nome

    cliente.send(bytes(welcome_messages, "utf8"))

    #Mensagem enviada a todos os usuários conectados ao chat através da função broadcast, basicamente informa que um usuário se conectou ao chat:
    msg = "%s se juntou ao chat!" % nome
    broadcast(bytes(msg, "utf8"))
    clientes[cliente] = nome

    #Laço que irá determinar o tipo de comando enviado pelo usuário e irá aplicar suas respectivas funcionalidades:
    while True:
        #Mensagem será recebida pelo servidor e usaremos o método split para separar os comandos do conteúdo da mensagem
        msg = cliente.recv(BUFSIZ)
        msg = msg.decode("utf8")
        msg = msg.split()
        print(msg)
        #COMANDOS SEND:
        #Comandos usados para enviar mensagens para todo o chat ou para um usuário em específico 
        if msg[0] == "send":
            #Comando do tipo send -all usado para enviar mensagens para todos os usuários do chat
            if msg[1] == "-all":
                client_ip = None
                client_port = None
                msg_content = ""
                #Laço no qual iremos atribuir o conteúdo da mensagem para a variável msg_content:
                for i in range(2, len(msg)):
                    msg_content += (msg[i] + " ")
                #Laço usado para obter o ip e porta do cliente, que está enviando a mensagem, através do dicionário de clientes:
                for sockets in clientes.keys():
                    if clientes[sockets] == nome:
                        client_ip, client_port = sockets.getpeername()
                #Obtendo data e hora de envio da mensagem:
                dt_string = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                #Mensagem final enviada para todos os usuários do chat utilizando a função broadcast:	
                broadcast(bytes(client_ip + ':' + str(client_port) + '/~' + nome + ": " + msg_content + dt_string, "utf8"))

            #Comando do tipo send -user usado para enviar mensagens para um usuário específico 
            elif msg[1] == "-user":
                if msg[2] in clientes.values():
                    receiver = None
                    client_ip = None
                    client_port = None
                    msg_content = ""
                    #Laço no qual iremos atribuir o conteúdo da mensagem para a variável msg_content:
                    for i in range(3, len(msg)):
                        msg_content += (msg[i] + " ")
                    #Laço usado para obter o ip e porta do cliente, que está enviando a mensagem, através do dicionário de clientes
                    #também será obtido o socket referente ao destinatário da mensagem:
                    for sockets in clientes.keys():
                        if clientes[sockets] == nome:
                            client_ip, client_port = sockets.getpeername()
                        if clientes[sockets] == msg[2]:
                            receiver = sockets
                    #Obtendo data e hora de envio da mensagem:
                    dt_string = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                    #Mensagem final que é mostrada tanto para o próprio usuário que a enviou como para o destinatário da mensagem:
                    cliente.send(bytes("/~Você: " + msg_content + " " + dt_string, "utf8"))	
                    receiver.send(bytes(client_ip + ':' + str(client_port) + '/~' +  nome + ": " + msg_content + " " + dt_string, "utf8"))
                #Caso o usuário não exista na lista de usuários será enviada a seguinte mensagem pelo servidor:
                else:
                    temp = "Usuario nao existente!"
                    cliente.send(bytes(temp, "utf8"))
            #Caso o comando do tipo send seja inválido será enviada a seguinte mensagem pelo servidor:
            else:
                temp = "Comando invalido"
                cliente.send(bytes(temp, "utf8"))
        #COMANDO LIST:
        #Irá retornar a lista de usuários conectados ao chat para o usuário
        elif msg[0] == "list":
            temp = "Usuarios disponiveis:"
            for cur_socket in clientes.keys():
                temp = temp + " %s" % clientes[cur_socket]
            cliente.send(bytes(temp, "utf8"))
        #COMANDO BYE:
        #Irá desconectar o usuário do chat
        elif msg[0] == "bye":
            #Enviará uma mensagem ao desconectar o usuário do chat:
            cliente.send(bytes("Você foi desconectado!!", "utf8"))
            cliente.close()
            #Deletando o usuário do dicionário de clientes:
            del clientes[cliente]
            #Mensagem enviada para todos os usuários do chat com o intuito de informar que um dos usuários desconectou-se do chat
            broadcast(bytes("%s saiu do chat" % nome, "utf8"))
            break
        #Caso o comando do usuário seja inválido será enviada a seguinte mensagem pelo servidor:
        else:
            cliente.send(bytes("Comando inválido!", "utf8"))

#Função criada para enviar uma dada mensagem a todos os usuários conectados ao chat
def broadcast(msg, prefixo=""):

    for socket in clientes:
        socket.send(bytes(prefixo, "utf8")+msg)

#Definindo algumas constantes que serão usadas ao longo do desenvolvimento do servidor
clientes = {}

HOST = ''
PORT = 33000
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