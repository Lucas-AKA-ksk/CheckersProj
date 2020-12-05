import threading
import pygame

from checkers.network import Network
from checkers.constants import WIDTH, HEIGHT, SQUARE_SIZE, RED, WHITE
from checkers.board import Board
from checkers.game import Game

FPS = 60
opponent_waiting = threading.Event()
turn_wait = threading.Event()
client = None
opponent_moves = []

def connect_to_server():

    """
    Inicializa o cliente,
    inicializa a thread responsável pelo recebimento
    e interpretação das mensagens do server e aguada por um adversário
    """

    global client
    client = Network()
    if client:
        talk_to_server = threading.Thread(target=handle_server_messages, args=(client,), daemon=True)
        talk_to_server.start()
        # Esperando o server autorizar o inicio do jogo (usando Thread Events)
        print("Waiting for an opponent...")
        opponent_waiting.wait()
        print("Opponent found, starting match...")
        return
    #fecha o programa em caso de erro
    else:
        exit()

def handle_server_messages(sock):

    """
    Recebe mensagens do servidor, interpreta e realiza a ação correspondente.
    """

    while True:
        # Recebe a mensagem através do método receive_data(network.py).
        server_msg = sock.receive_data()

        # Se a mensagem for vazia, quebra o loop (conexão perdida ou fechada pelo server).
        if not server_msg:
            print("[ERROR] Lost connection to server, close your game...")
            break

        # Atribui um id de acordo com a mensagem do servidor.
        if server_msg.startswith("You're playing as"):
            if server_msg == "You're playing as red.":
                sock.id = RED
                print(server_msg)
            else:
                sock.id = WHITE
                print(server_msg)

        # autoriza o cliente a iniciar o jogo (liberando o evento da thread).
        if server_msg == "Start game":
            print(server_msg)
            opponent_waiting.set()

        # Se a mensagem se inicia com '[', ela contem os movimentos
        # feitos pelo adversário, que são armazenados em uma variável
        # global, e serão utilizadas em main(). O evento turn_wait é
        # liberado aqui.
        if server_msg.startswith("["):
            global opponent_moves
            opponent_moves = server_msg[2:9].split('/')
            print("opponent moves = " , opponent_moves)
            turn_wait.set()
            turn_wait.clear()

    # conexão é fechada
    sock.close()

def get_row_col_from_mouse(pos):
    """
    Função que separa as coordenadas do mouse,
    realiza uma floor division de modo a obter
    a linha e coluna correspondente ao espaço na tela selecionado.
    """
    x, y = pos
    row = y // SQUARE_SIZE
    col = x // SQUARE_SIZE
    return row, col

def main():

    player_move = "" # armazena os movimentos feitos pelo jogador na rodada
    run = True
    clock = pygame.time.Clock()
    game = Game(WIN)

    while run:
        clock.tick(FPS)
        game.update()

        # Verifica se há um vencedor
        if game.winner() != None:
            print("Player ",game.winner(), "won the match!!")
            break
            #run = False

        # Se for a vez do adversário,
        # aguarda a thread handle_server_messages()
        # receber o movimento feito pelo adversário,
        # e o repete neste cliente, sincronizando os jogos
        if client.id != game.turn:
            print("Waiting for your opponent to move...")
            turn_wait.wait()
            game.select(int(opponent_moves[0]),int(opponent_moves[1]))
            game.select(int(opponent_moves[2]),int(opponent_moves[3]))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False


            if event.type == pygame.MOUSEBUTTONDOWN:
                if client.id == game.turn:
                    pos = pygame.mouse.get_pos()
                    row, col = get_row_col_from_mouse(pos)
                    move = game.select(row, col)

                    # Valor 1 significa que uma peça foi selecionada
                    if move == 1:

                        # Primeira coordenada de movimento é adicionada à variável,
                        # essa operação pode repetir várias vezes
                        player_move = '[/' + str(row) + '/' + str(col)
                        print("piece selected = ", player_move)

                    # Valor 2 significa que uma coordenada valida para movimentaćão da peça foi selecionada
                    elif move == 2:

                        # Segunda coordenada de movimento é adicionada à variável
                        # e enviada para o servidor, essa operação só ocorre uma vez
                        player_move += '/' + str(row) + '/' + str(col) + '/]'
                        print("player moves = ", player_move)
                        client.send_data(player_move)

                else:
                    print("You must wait for your turn...")

    client.close()
    pygame.quit()

connect_to_server()

# Criando a tela de jogo
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Checkers')

main()
