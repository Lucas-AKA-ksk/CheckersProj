import socket
from .constants import HEADERSIZE


class Network:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = socket.gethostbyname(socket.gethostname())
        self.port = 5555
        self.addr = (self.server, self.port)
        self.id = None
        self.connect()

    def get_id(self):
        return self.id

    def connect(self):
        try:
            self.client.connect(self.addr)
        except socket.error as msg:
            print("[ERROR] Caught exception socket.error : %s" %msg)
            exit()

    def close(self):
        self.client.close()

    def send_data(self,data):

        """Adiciona um Header à mensagem que especifica
         o tamanho da mesma, em bytes, e envia ao server.
        """

        data_with_header = f"{len(data):<{HEADERSIZE}}" + data
        self.client.send(bytes(data_with_header, "utf-8"))

    def receive_data(self):

        """
        Recebe o Header da mensagem (tamanho max. de 10 bytes),
        altera o tamanho do buffer de acordo com o tamanho da mensagem real,
        recebe, separa e retorna a mensagem.
        """

        full_data = ''
        new_data = True
        buffer_size = 10

        while True:

            # Recebe os primeiros 10 bytes(Header) da mensagem no primeiro loop
            # Recebe N bytes da mensagem no segundo loop
            data = self.client.recv(buffer_size)

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
