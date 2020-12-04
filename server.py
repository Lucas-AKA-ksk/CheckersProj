import socket
import threading
from checkers.constants import HEADERSIZE


server = socket.gethostbyname(socket.gethostname())
port = 5555
addr = (server, port)
all_conn = []
all_addr = []


def sock_init():

    """
    Inicialização do socket
    """

    new_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    new_sock.bind(addr)
    new_sock.listen(2)
    return new_sock

def send_data(receiver, data):

    """Adiciona um Header à mensagem que especifica
     o tamanho da mesma, em bytes, e envia ao cliente.
    """

    data_with_header = f"{len(data):<{HEADERSIZE}}" + data
    receiver.send(bytes(data_with_header, "utf-8"))

def receive_data(sender):

    """
    Recebe o Header da mensagem (tamanho fixo de 10 bytes),
    altera o tamanho do buffer de acordo com o tamanho da mensagem real,
    recebe, separa e retorna a mensagem.
    """

    full_data = ''
    new_data = True
    buffer_size = 10

    while True:

        # Recebe os primeiros 10 bytes(Header) da mensagem no primeiro loop
        # Recebe N bytes da mensagem no segundo loop
        data = sender.recv(buffer_size)

        if new_data:

            # buffer_size passa a ser do mesmo tamanho da mensagem
            data_len = int(data[:HEADERSIZE])
            buffer_size = data_len

            new_data = False

        full_data += data.decode("utf-8")

        if len(full_data)-HEADERSIZE == data_len:

            # Retira-se o Header da mensagem e retorna a mensagem
            full_data = full_data[HEADERSIZE:]
            return full_data

def pairing_players(conn_1, conn_2, player_1, player_2):

    """Atribui IDs(cores) aos jogadores, autoriza o inicio da partida
    e inicia threads para manipular as mensagens dos dois jogadores conectados."""

    print("[MATCH]Match started between ", player_1, "and ", player_2)
    send_data(conn_1,"You're playing as red.")
    send_data(conn_2,"You're playing as white.")
    send_data(conn_1,"Start game")
    send_data(conn_2,"Start game")
    talk_to_1 = threading.Thread(target=message_handling, args=(conn_1,conn_2,))
    talk_to_2 = threading.Thread(target=message_handling, args=(conn_2,conn_1,))
    talk_to_1.start()
    talk_to_2.start()

def message_handling(sender, receiver):

    """
    Recebe as mensagens de um cliente e repassa para o outro.
    """

    while True:

        msg = receive_data(sender)

        # Conexão com cliente perdida
        if not msg:
            break

        # Formado de mensagem que representa a coordenada do movimento do jogador
        if msg.startswith("["):
            print("sending movement")
            send_data(receiver, msg)

    sender.close()

def accepting_connections():

    """
    Executa constantemente aceitando conexões,
    a cada dois jogadores conectados,
    um jogo é iniciado entre eles.
    """

    print("[SERVER INITIATED] Waiting for connections...")

    # fecha todas as conexões listadas (em caso de server reboot)
    for conn in all_conn:
        conn.close()

    # esvazia as listas de conns e addrs (em caso de server reboot)
    del all_conn[:]
    del all_addr[:]

    players = 0

    while True:
        try:
            conn, clnt_addr = sock.accept()
            send_data(conn,"Welcome player!")

            # Adiciona ip e porta às respectivas listas
            all_conn.append(conn)
            all_addr.append(clnt_addr)

            print("[NEW CONNECTION] Connected to:", clnt_addr)

            # a cada 2 clients conectados se inicia uma nova partida (utilizando uma thread)
            if len(all_addr) % 2 == 0:
                game = threading.Thread(target=pairing_players, args=(all_conn[len(all_conn) - 2],all_conn[len(all_conn) - 1],all_addr[len(all_addr) - 2],all_addr[len(all_addr) -1],), daemon=True)
                game.start()
            else:
                send_data(conn,"Waiting for another player...")

            players += 1

        except socket.error as msg:
            print("[ERROR] Caught exception socket.error : %s" %msg)
            exit()


sock = sock_init()
accepting_connections()
