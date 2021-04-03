import threading
import time

import typer
import zmq

from chat_client import ChatClient
from chat_screen import ChatScreen
from chat_server import ChatServer

app = typer.Typer()


def screen_recv(chat_recv: zmq.Socket):
    while True:
        print(chat_recv.recv_string())


def screen_send(username: str, chat_sender: zmq.Socket):
    while True:
        s = input(f'{username}: ')
        if s is not None and s != "":
            chat_sender.send_string(s)
        time.sleep(0.005)


@app.command()
def serve(host: str = '*', port: int=8888, screen_host: str = '*', screen_port: int = 8889):                            
    server = ChatServer(host, port, screen_host, screen_port)
    try:
        server.run()
    except KeyboardInterrupt:
        pass

@app.command()
def connect(username: str, host: str = 'localhost', port: int=8888, screen_port: int = 8889):
    # Create a pipe for de io communication
    receiver = zmq.Context().instance().socket(zmq.PAIR)
    receiver.bind("inproc://clientchat")

    sender = zmq.Context().instance().socket(zmq.PAIR)
    sender.connect("inproc://clientchat")
    
    client = ChatClient(username, host, port, receiver)
    client.run_concurrent()

    display_receiver = zmq.Context().instance().socket(zmq.PAIR)
    display_receiver.bind("inproc://clientdisplay")
    
    display_sender = zmq.Context().instance().socket(zmq.PAIR)
    display_sender.connect("inproc://clientdisplay")
    
    display = ChatScreen(host, screen_port, display_sender)
    display.run_concurrent()

    screen_recv_thread = threading.Thread(target=screen_recv, args=(display_receiver,))
    screen_recv_thread.daemon = True
    screen_recv_thread.start()

    screen_send_thread = threading.Thread(target=screen_send, args=(username, sender))
    screen_send_thread.daemon = True
    screen_send_thread.start()

    screen_recv_thread.join()
    screen_send_thread.join()


if '__main__' == __name__:
    try:
        app()
    except KeyboardInterrupt as e:
        pass
    except:
        raise
